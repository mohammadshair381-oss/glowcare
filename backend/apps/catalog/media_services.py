from __future__ import annotations

import hashlib

from django.db.models import Q

from .models import MediaAsset


def compute_sha256(uploaded_file) -> str:
  h = hashlib.sha256()
  try:
    for chunk in uploaded_file.chunks():
      if chunk:
        h.update(chunk)
  finally:
    try:
      uploaded_file.seek(0)
    except Exception:
      pass
  return h.hexdigest()


def create_media_asset(
  *,
  file,
  kind: str = "image",
  title: str = "",
  alt: str = "",
  context: str = MediaAsset.Context.TEMP,
  cms_section: str = "",
  product_category: str = "",
  product_subcategory: str = "",
):
  """
  Creates a MediaAsset with structured storage + duplicate detection.
  Returns (asset, created_bool, duplicate_bool).
  """

  kind = (kind or "image").lower()
  if kind not in ["image", "video"]:
    kind = "image"

  sha = compute_sha256(file)
  size = getattr(file, "size", None)
  ctype = getattr(file, "content_type", "") or ""
  orig = getattr(file, "name", "") or ""

  existing = MediaAsset.objects.filter(sha256=sha, kind=kind).order_by("-created_at").first()
  if existing:
    size_ok = size is None or existing.size_bytes is None or existing.size_bytes == size
    ctype_ok = not ctype or not existing.content_type or existing.content_type == ctype
    if size_ok and ctype_ok:
      return existing, False, True

  asset = MediaAsset(
    kind=kind,
    context=context or MediaAsset.Context.TEMP,
    cms_section=str(cms_section or "")[:80],
    product_category=str(product_category or "")[:80],
    product_subcategory=str(product_subcategory or "")[:80],
    sha256=sha,
    original_filename=str(orig or "")[:240],
    content_type=str(ctype or "")[:120],
    size_bytes=size if isinstance(size, int) else None,
    title=(title or "")[:120],
    alt=(alt or "")[:180],
  )
  asset.file = file
  asset.save()
  return asset, True, False


def media_asset_usage(asset: MediaAsset) -> dict:
  """
  Returns a structured usage summary for warnings / delete guards.
  """
  # catalog
  primary_products = asset.primary_for_products.all()
  gallery = asset.product_images.all()

  # cms
  hero_bg = asset.hero_backgrounds.all()
  hero_a = asset.hero_card_a.all()
  hero_b = asset.hero_card_b.all()
  hero_c = asset.hero_card_c.all()
  logos = asset.featured_logos.all()
  avatars = asset.testimonial_avatars.all()

  return {
    "products": {
      "primary_media": {"count": primary_products.count(), "ids": list(primary_products.values_list("id", flat=True)[:12])},
      "gallery": {"count": gallery.count(), "ids": list(gallery.values_list("product_id", flat=True)[:12])},
    },
    "homepage": {
      "hero_backgrounds": {"count": hero_bg.count(), "ids": list(hero_bg.values_list("id", flat=True)[:12])},
      "hero_card_a": {"count": hero_a.count(), "ids": list(hero_a.values_list("id", flat=True)[:12])},
      "hero_card_b": {"count": hero_b.count(), "ids": list(hero_b.values_list("id", flat=True)[:12])},
      "hero_card_c": {"count": hero_c.count(), "ids": list(hero_c.values_list("id", flat=True)[:12])},
    },
    "banners": {},
    "brands": {"featured_logos": {"count": logos.count(), "ids": list(logos.values_list("id", flat=True)[:12])}},
    "cms_sections": {"testimonial_avatars": {"count": avatars.count(), "ids": list(avatars.values_list("id", flat=True)[:12])}},
    "total_links": (
      primary_products.count()
      + gallery.count()
      + hero_bg.count()
      + hero_a.count()
      + hero_b.count()
      + hero_c.count()
      + logos.count()
      + avatars.count()
    ),
  }


def search_assets_queryset(q: str):
  qs = MediaAsset.objects.all()
  q = (q or "").strip()
  if not q:
    return qs
  return qs.filter(
    Q(title__icontains=q)
    | Q(alt__icontains=q)
    | Q(original_filename__icontains=q)
    | Q(file__icontains=q)
    | Q(sha256__icontains=q)
  )
