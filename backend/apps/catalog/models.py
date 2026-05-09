from django.db import models
from django.utils.text import slugify


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
  Stored in MEDIA_ROOT/uploads/<yyyy>/<mm>/...
  """

  class Kind(models.TextChoices):
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"

  kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.IMAGE)
  file = models.FileField(upload_to="uploads/%Y/%m/")
  alt = models.CharField(max_length=180, blank=True)
  title = models.CharField(max_length=120, blank=True)
  width = models.PositiveIntegerField(null=True, blank=True)
  height = models.PositiveIntegerField(null=True, blank=True)

  def __str__(self):
    return self.title or self.file.name


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
  category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
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
  is_active = models.BooleanField(default=True)

  class Meta:
    unique_together = [("product", "sku")]
    ordering = ["id"]

  def __str__(self):
    return f"{self.product.name} — {self.sku}"

