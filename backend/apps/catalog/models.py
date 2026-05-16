from django.db import models
from django.utils.text import slugify

from .media_storage import media_asset_upload_to


class TimeStampedModel(models.Model):
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    abstract = True


class Category(TimeStampedModel):
  name = models.CharField(max_length=80, unique=True)
  slug = models.SlugField(max_length=100, unique=True, blank=True)
  description = models.TextField(blank=True)
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ["name"]

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)


class Brand(TimeStampedModel):
  name = models.CharField(max_length=80, unique=True)
  slug = models.SlugField(max_length=100, unique=True, blank=True)
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ["name"]

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)


class SubCategory(TimeStampedModel):
  category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="subcategories")
  name = models.CharField(max_length=80)
  slug = models.SlugField(max_length=110, blank=True)
  is_active = models.BooleanField(default=True)

  class Meta:
    ordering = ["category__name", "name"]
    unique_together = [("category", "slug")]

  def __str__(self):
    return f"{self.category.slug}/{self.slug}"

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)[:105]
    super().save(*args, **kwargs)


class Tag(TimeStampedModel):
  name = models.CharField(max_length=50, unique=True)
  slug = models.SlugField(max_length=60, unique=True, blank=True)

  class Meta:
    ordering = ["name"]

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)


class MediaAsset(TimeStampedModel):
  """
  Shared media library asset.
  Stored in MEDIA_ROOT/uploads/<kind>/<context>/<...>/<yyyy>/<mm>/...
  """

  class Kind(models.TextChoices):
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"

  class Context(models.TextChoices):
    HOMEPAGE = "homepage", "Homepage"
    BANNERS = "banners", "Banners"
    BRANDS = "brands", "Brands"
    PRODUCTS = "products", "Products"
    PROMOS = "promos", "Promos"
    CMS_SECTIONS = "cms_sections", "CMS sections"
    TEMP = "temp", "Temp"

  kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.IMAGE)
  context = models.CharField(max_length=32, choices=Context.choices, default=Context.TEMP)
  cms_section = models.CharField(max_length=80, blank=True, default="")
  product_category = models.CharField(max_length=80, blank=True, default="")
  product_subcategory = models.CharField(max_length=80, blank=True, default="")

  sha256 = models.CharField(max_length=64, blank=True, db_index=True, default="")
  original_filename = models.CharField(max_length=240, blank=True, default="")
  content_type = models.CharField(max_length=120, blank=True, default="")
  size_bytes = models.BigIntegerField(null=True, blank=True)

  file = models.FileField(upload_to=media_asset_upload_to)
  alt = models.CharField(max_length=180, blank=True)
  title = models.CharField(max_length=120, blank=True)
  width = models.PositiveIntegerField(null=True, blank=True)
  height = models.PositiveIntegerField(null=True, blank=True)

  def __str__(self):
    return self.title or self.file.name

  def delete(self, *args, **kwargs):
    storage = getattr(self.file, "storage", None)
    name = getattr(self.file, "name", "") or ""
    super().delete(*args, **kwargs)
    if storage and name:
      try:
        storage.delete(name)
      except Exception:
        # best-effort cleanup; DB delete already succeeded
        pass


class Product(TimeStampedModel):
  """
  CMS-driven product model. Used by frontend via /api/v1/products/.
  """

  class Badge(models.TextChoices):
    NEW = "New", "New"
    BESTSELLER = "Bestseller", "Bestseller"
    TRENDING = "Trending", "Trending"
    HOT = "Hot", "Hot"
    FEATURED = "Featured", "Featured"

  sku = models.CharField(max_length=40, unique=True)
  name = models.CharField(max_length=140)
  slug = models.SlugField(max_length=180, unique=True, blank=True)
  brand = models.CharField(max_length=80, default="GlowCare")
  brand_ref = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name="products")
  category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
  subcategory = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.PROTECT, related_name="products")
  description = models.TextField(blank=True)

  price = models.PositiveIntegerField(help_text="Price in INR (integer)")
  compare_at_price = models.PositiveIntegerField(null=True, blank=True, help_text="Original MRP (optional)")
  badge = models.CharField(max_length=24, choices=Badge.choices, blank=True)

  rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
  reviews_count = models.PositiveIntegerField(default=0)

  is_active = models.BooleanField(default=True)
  is_published = models.BooleanField(default=True)

  tags = models.ManyToManyField(Tag, blank=True, related_name="products")
  concern_tags = models.JSONField(default=list, blank=True)
  skin_type_tags = models.JSONField(default=list, blank=True)
  ingredients = models.JSONField(default=list, blank=True)

  primary_media = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="primary_for_products")

  class Meta:
    ordering = ["-updated_at"]

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.name)[:175]
    super().save(*args, **kwargs)


class ProductImage(TimeStampedModel):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
  media = models.ForeignKey(MediaAsset, on_delete=models.PROTECT, related_name="product_images")
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return f"{self.product_id} image {self.id}"


class Variant(TimeStampedModel):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
  sku = models.CharField(max_length=50)
  shade = models.CharField(max_length=80, blank=True, default="Original")
  size_ml = models.PositiveIntegerField(null=True, blank=True)
  stock = models.PositiveIntegerField(default=0)
  track_inventory = models.BooleanField(default=True)
  low_stock_threshold = models.PositiveIntegerField(default=5)
  is_active = models.BooleanField(default=True)

  class Meta:
    unique_together = [("product", "sku")]
    ordering = ["id"]

  def __str__(self):
    return f"{self.product.name} — {self.sku}"
