from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime

from django.utils.text import slugify


_FILENAME_SAFE_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_ext(filename: str) -> str:
  _, ext = os.path.splitext(filename or "")
  ext = (ext or "").lower()
  if ext and len(ext) <= 12 and ext.startswith("."):
    return ext
  return ""


def sanitize_basename(filename: str) -> str:
  base = os.path.basename(filename or "").strip() or "upload"
  base = _FILENAME_SAFE_RE.sub("-", base)
  base = base.strip("-._") or "upload"
  return base[:120]


def kind_dir(kind: str) -> str:
  return "videos" if (kind or "").lower() == "video" else "images"


def _norm_slug(val: str) -> str:
  s = slugify(str(val or "").strip())[:60]
  return s or "other"


@dataclass(frozen=True)
class UploadPlacement:
  context: str
  cms_section: str | None = None
  product_category: str | None = None
  product_subcategory: str | None = None


def media_asset_upload_to(instance, filename: str) -> str:
  """
  Professional structured storage layout (MEDIA_ROOT/uploads/...).
  Uses instance fields (kind/context/category/etc) and prefers instance.sha256.
  """

  now = datetime.utcnow()
  y = f"{now.year:04d}"
  m = f"{now.month:02d}"

  ctx = (getattr(instance, "context", "") or "temp").strip()
  ctx_slug = _norm_slug(ctx)

  parts: list[str] = ["uploads", kind_dir(getattr(instance, "kind", "")), ctx_slug]

  pc = (getattr(instance, "product_category", "") or "").strip()
  if pc:
    parts.append(_norm_slug(pc))
    psc = (getattr(instance, "product_subcategory", "") or "").strip()
    if psc:
      parts.append(_norm_slug(psc))

  sec = (getattr(instance, "cms_section", "") or "").strip()
  if sec:
    parts.append(_norm_slug(sec))

  # light bucketing to avoid huge single directories
  parts.extend([y, m])

  sha = (getattr(instance, "sha256", "") or "").strip().lower()
  stem = sanitize_basename(filename)
  ext = _safe_ext(filename)
  if sha and len(sha) >= 16:
    name = f"{sha[:16]}-{slugify(stem)[:80] or 'asset'}{ext}"
  else:
    name = f"{slugify(stem)[:80] or 'asset'}{ext}"

  return "/".join(parts + [name])

