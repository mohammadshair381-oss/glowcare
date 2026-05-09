from rest_framework import serializers

from apps.catalog.models import Product, Variant


class VariantSerializer(serializers.ModelSerializer):
  sizeMl = serializers.IntegerField(source="size_ml", allow_null=True, required=False)

  class Meta:
    model = Variant
    fields = ["sku", "shade", "sizeMl", "stock", "is_active"]


class ProductSerializer(serializers.ModelSerializer):
  category = serializers.CharField(source="category.slug")
  image = serializers.SerializerMethodField()
  gallery = serializers.SerializerMethodField()
  badge = serializers.CharField()
  rating = serializers.SerializerMethodField()
  reviewsCount = serializers.IntegerField(source="reviews_count")
  skinTypeTags = serializers.JSONField(source="skin_type_tags")
  concernTags = serializers.JSONField(source="concern_tags")
  variants = VariantSerializer(many=True)

  class Meta:
    model = Product
    fields = [
      "id",
      "sku",
      "name",
      "brand",
      "category",
      "price",
      "compare_at_price",
      "badge",
      "description",
      "image",
      "gallery",
      "rating",
      "reviewsCount",
      "ingredients",
      "skinTypeTags",
      "concernTags",
      "variants",
    ]

  def get_image(self, obj: Product):
    if obj.primary_media_id:
      return obj.primary_media.file.url
    first = obj.images.order_by("sort_order").first()
    if first:
      return first.media.file.url
    return ""

  def get_gallery(self, obj: Product):
    urls = []
    if obj.primary_media_id:
      urls.append(obj.primary_media.file.url)
    for pi in obj.images.order_by("sort_order", "id").all()[:12]:
      if pi.media_id and pi.media.file:
        urls.append(pi.media.file.url)
    # de-dupe preserving order
    seen = set()
    out = []
    for u in urls:
      if not u or u in seen:
        continue
      seen.add(u)
      out.append(u)
    return out

  def get_rating(self, obj: Product):
    try:
      return float(obj.rating)
    except Exception:
      return 0.0
