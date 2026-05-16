import ast
import os
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import Category, MediaAsset, Product, ProductImage, Variant


@dataclass(frozen=True)
class ImportStats:
  categories_created: int = 0
  products_created: int = 0
  products_updated: int = 0
  variants_created: int = 0
  images_created: int = 0
  media_created: int = 0


def _extract_js_array(source: str, marker: str) -> str:
  """
  Extract a JS array literal starting at `marker` (e.g. "const X = [").
  Handles nested []/{} and quoted strings.
  Returns the substring including the outer [ ... ].
  """
  idx = source.find(marker)
  if idx < 0:
    raise CommandError(f"Could not find marker: {marker!r}")
  start = source.find("[", idx)
  if start < 0:
    raise CommandError("Could not find '[' after marker.")

  depth = 0
  in_str = None
  esc = False
  for i in range(start, len(source)):
    ch = source[i]
    if in_str:
      if esc:
        esc = False
        continue
      if ch == "\\":
        esc = True
        continue
      if ch == in_str:
        in_str = None
      continue

    if ch == '"' or ch == "'":
      in_str = ch
      continue
    if ch == "[":
      depth += 1
      continue
    if ch == "]":
      depth -= 1
      if depth == 0:
        return source[start : i + 1]
      continue

  raise CommandError("Unterminated array literal while extracting catalog.")


def _js_object_literal_to_python_literal(js: str) -> str:
  """
  Convert a restricted JS object/array literal into a Python literal:
  - Quotes unquoted object keys (e.g. { id: "x" } -> { "id": "x" })
  - Converts true/false/null to True/False/None
  Assumes input contains only literals (no functions/identifiers besides keys).
  """
  out: list[str] = []
  in_str = None
  esc = False
  i = 0
  n = len(js)

  def is_ident_start(c: str) -> bool:
    return c.isalpha() or c == "_"

  def is_ident(c: str) -> bool:
    return c.isalnum() or c == "_"

  while i < n:
    ch = js[i]
    if in_str:
      out.append(ch)
      if esc:
        esc = False
      elif ch == "\\":
        esc = True
      elif ch == in_str:
        in_str = None
      i += 1
      continue

    if ch == '"' or ch == "'":
      in_str = ch
      out.append(ch)
      i += 1
      continue

    if is_ident_start(ch):
      # Potentially a key or a literal token (true/false/null).
      j = i + 1
      while j < n and is_ident(js[j]):
        j += 1
      token = js[i:j]

      k = j
      while k < n and js[k].isspace():
        k += 1
      if k < n and js[k] == ":":
        out.append('"')
        out.append(token)
        out.append('"')
        out.append(":")
        i = k + 1
        continue

      if token == "true":
        out.append("True")
      elif token == "false":
        out.append("False")
      elif token == "null":
        out.append("None")
      else:
        out.append(token)
      i = j
      continue

    out.append(ch)
    i += 1

  return "".join(out)


def _load_frontend_catalog(repo_root: Path, source_path: Path) -> list[dict]:
  if not source_path.exists():
    raise CommandError(f"Source not found: {source_path}")
  raw = source_path.read_text(encoding="utf-8")
  arr = _extract_js_array(raw, "const DEFAULT_PRODUCT_CATALOG")
  py_lit = _js_object_literal_to_python_literal(arr)
  try:
    data = ast.literal_eval(py_lit)
  except Exception as e:
    raise CommandError(f"Failed to parse DEFAULT_PRODUCT_CATALOG from {source_path}: {e}") from e
  if not isinstance(data, list):
    raise CommandError("Parsed catalog is not a list.")
  out = []
  for item in data:
    if isinstance(item, dict):
      out.append(item)
  if not out:
    raise CommandError("Parsed catalog is empty.")
  return out


def _sku_from_legacy_id(legacy_id: str, name: str) -> str:
  s = str(legacy_id or "")
  m = re.search(r"(\\d{2,})", s)
  if m:
    return f"GC-{m.group(1)}"[:40]
  base = slugify(name or "product")[:30] or "product"
  return f"GC-{base}".upper()[:40]


def _path_from_repo(repo_root: Path, rel_or_url: str) -> Path | None:
  raw = str(rel_or_url or "").strip()
  if not raw:
    return None
  if raw.startswith("http://") or raw.startswith("https://"):
    return None
  raw = raw.lstrip("/")
  return repo_root / raw


class Command(BaseCommand):
  help = "Seed Django catalog products from the existing frontend demo catalog (js/main.js DEFAULT_PRODUCT_CATALOG)."

  def add_arguments(self, parser):
    parser.add_argument(
      "--source",
      default="js/main.js",
      help="Path (repo-relative) to the frontend JS file containing DEFAULT_PRODUCT_CATALOG. Default: js/main.js",
    )
    parser.add_argument(
      "--update-existing",
      action="store_true",
      help="Update existing products (matched by sku) to match frontend demo values.",
    )
    parser.add_argument(
      "--skip-media",
      action="store_true",
      help="Do not import/copy images into MediaAsset; keeps primary_media empty.",
    )
    parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Parse and report what would be created without writing to the database.",
    )

  @transaction.atomic
  def handle(self, *args, **opts):
    repo_root = Path(settings.BASE_DIR).parent
    source_path = repo_root / str(opts["source"])

    catalog = _load_frontend_catalog(repo_root, source_path)

    stats = ImportStats()
    categories_cache: dict[str, Category] = {}
    media_cache: dict[str, MediaAsset] = {}

    def bump(**kwargs):
      nonlocal stats
      stats = ImportStats(**{**stats.__dict__, **kwargs})

    if opts["dry_run"]:
      self.stdout.write(self.style.WARNING("DRY RUN: no database changes will be committed."))

    for p in catalog:
      legacy_id = str(p.get("id") or "")
      name = str(p.get("name") or "").strip()
      if not legacy_id or not name:
        continue

      cat_slug = str(p.get("category") or "skincare").strip().lower() or "skincare"
      if cat_slug not in categories_cache:
        if opts["dry_run"]:
          cat = Category(name=cat_slug, slug=cat_slug)
          created = Category.objects.filter(slug=cat_slug).exists() is False
        else:
          cat, created = Category.objects.get_or_create(name=cat_slug, defaults={"slug": cat_slug})
        categories_cache[cat_slug] = cat
        if created:
          bump(categories_created=stats.categories_created + 1)
      category = categories_cache[cat_slug]

      sku = _sku_from_legacy_id(legacy_id, name)
      defaults = {
        "name": name,
        "brand": str(p.get("brand") or "GlowCare")[:80],
        "category": category,
        "description": str(p.get("description") or ""),
        "price": int(p.get("price") or 0),
        "compare_at_price": int(p.get("compare_at_price") or 0) or None,
        "badge": str(p.get("badge") or "")[:24],
        "rating": Decimal(str(p.get("rating") or 0)),
        "reviews_count": int(p.get("reviewsCount") or p.get("reviews_count") or 0),
        "ingredients": p.get("ingredients") or [],
        "skin_type_tags": p.get("skinTypeTags") or p.get("skin_type_tags") or [],
        "concern_tags": p.get("concernTags") or p.get("concern_tags") or [],
        "is_active": True,
        "is_published": True,
      }

      if opts["dry_run"]:
        existing = Product.objects.filter(sku=sku).first()
        created = existing is None
        prod = existing or Product(sku=sku, **defaults)
      else:
        prod, created = Product.objects.get_or_create(sku=sku, defaults=defaults)

      if created:
        bump(products_created=stats.products_created + 1)
      elif opts["update_existing"]:
        changed_fields = []
        for k, v in defaults.items():
          if k == "category":
            if getattr(prod, "category_id", None) != v.id:
              setattr(prod, k, v)
              changed_fields.append(k)
          else:
            if getattr(prod, k, None) != v:
              setattr(prod, k, v)
              changed_fields.append(k)
        if changed_fields and not opts["dry_run"]:
          prod.save(update_fields=changed_fields + ["updated_at"])
        if changed_fields:
          bump(products_updated=stats.products_updated + 1)

      # Media (primary + gallery)
      if not opts["skip_media"]:
        img_path = _path_from_repo(repo_root, p.get("image") or "")
        if img_path and img_path.exists():
          key = os.fspath(img_path)
          media = media_cache.get(key)
          if not media:
            if opts["dry_run"]:
              media = MediaAsset(kind=MediaAsset.Kind.IMAGE, alt=name[:180], title=name[:120])
            else:
              media = MediaAsset.objects.create(kind=MediaAsset.Kind.IMAGE, alt=name[:180], title=name[:120])
              with img_path.open("rb") as f:
                media.file.save(img_path.name, File(f), save=True)
            media_cache[key] = media
            bump(media_created=stats.media_created + 1)
          if not getattr(prod, "primary_media_id", None) and not opts["dry_run"]:
            prod.primary_media = media
            prod.save(update_fields=["primary_media", "updated_at"])

        gallery = p.get("gallery") or []
        if isinstance(gallery, list) and gallery and not opts["dry_run"]:
          # Keep gallery in sync for demo seeded products by clearing only if update-existing is on.
          if opts["update_existing"]:
            ProductImage.objects.filter(product=prod).delete()
          sort = 0
          for g in gallery[:12]:
            gpath = _path_from_repo(repo_root, g)
            if not gpath or not gpath.exists():
              continue
            key = os.fspath(gpath)
            gmedia = media_cache.get(key)
            if not gmedia:
              gmedia = MediaAsset.objects.create(kind=MediaAsset.Kind.IMAGE, alt=name[:180], title=name[:120])
              with gpath.open("rb") as f:
                gmedia.file.save(gpath.name, File(f), save=True)
              media_cache[key] = gmedia
              bump(media_created=stats.media_created + 1)
            ProductImage.objects.create(product=prod, media=gmedia, sort_order=sort)
            sort += 1
            bump(images_created=stats.images_created + 1)

      # Variants
      variants = p.get("variants") or []
      if isinstance(variants, list) and variants:
        if opts["update_existing"] and not opts["dry_run"]:
          Variant.objects.filter(product=prod).delete()
        for v in variants[:24]:
          if not isinstance(v, dict):
            continue
          vsku = str(v.get("sku") or "").strip()
          if not vsku:
            continue
          shade = str(v.get("shade") or "Original")[:80]
          size_ml = v.get("sizeMl") or v.get("size_ml")
          size_ml = int(size_ml) if str(size_ml or "").isdigit() else None
          stock = int(v.get("stock") or 0)
          if opts["dry_run"]:
            exists = Variant.objects.filter(product=prod, sku=vsku).exists()
            if not exists:
              bump(variants_created=stats.variants_created + 1)
            continue
          _, v_created = Variant.objects.get_or_create(
            product=prod,
            sku=vsku,
            defaults={"shade": shade, "size_ml": size_ml, "stock": max(0, stock), "is_active": True},
          )
          if v_created:
            bump(variants_created=stats.variants_created + 1)

    if opts["dry_run"]:
      transaction.set_rollback(True)
      self.stdout.write(
        self.style.WARNING(
          "DRY RUN complete (rolled back): "
          f"categories +{stats.categories_created}, products +{stats.products_created} (would update {stats.products_updated}), "
          f"variants +{stats.variants_created}, media +{stats.media_created}, gallery images +{stats.images_created}."
        )
      )
      return

    self.stdout.write(
      self.style.SUCCESS(
        "Seeded products from frontend demo catalog: "
        f"categories +{stats.categories_created}, products +{stats.products_created} (updated {stats.products_updated}), "
        f"variants +{stats.variants_created}, media +{stats.media_created}, gallery images +{stats.images_created}."
      )
    )
