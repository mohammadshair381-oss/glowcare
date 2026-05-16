from rest_framework import serializers

from apps.catalog.models import Product, Variant
from apps.customers.cart_service import COUPONS, compute_totals
from apps.customers.models import Cart, CartItem, Order, OrderItem, ShippingAddress


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


class CartItemSerializer(serializers.ModelSerializer):
  productId = serializers.IntegerField(source="product_id", read_only=True)
  variantKey = serializers.CharField(source="variant_sku", read_only=True)
  product = serializers.SerializerMethodField()
  variant = serializers.SerializerMethodField()

  class Meta:
    model = CartItem
    fields = ["id", "productId", "variantKey", "qty", "product", "variant"]

  def get_product(self, obj: CartItem):
    p = obj.product
    image = ""
    if getattr(p, "primary_media_id", None):
      image = p.primary_media.file.url
    else:
      first = p.images.order_by("sort_order").first()
      if first:
        image = first.media.file.url
    return {"id": p.id, "name": p.name, "price": p.price, "image": image}

  def get_variant(self, obj: CartItem):
    p = obj.product
    v = p.variants.filter(sku=obj.variant_sku).first()
    if not v:
      return {"sku": obj.variant_sku, "shade": "", "sizeMl": None, "stock": 0, "is_active": False}
    return {"sku": v.sku, "shade": v.shade, "sizeMl": v.size_ml, "stock": v.stock, "is_active": v.is_active}


class CartSerializer(serializers.ModelSerializer):
  items = CartItemSerializer(many=True, read_only=True)
  coupon = serializers.SerializerMethodField()
  totals = serializers.SerializerMethodField()

  class Meta:
    model = Cart
    fields = ["id", "coupon_code", "coupon", "items", "totals"]

  def get_coupon(self, obj: Cart):
    code = (obj.coupon_code or "").upper()
    return COUPONS.get(code) if code else None

  def get_totals(self, obj: Cart):
    t = compute_totals(obj)
    return {"subtotal": t.subtotal, "discount": t.discount, "shipping": t.shipping, "total": t.total, "coupon": t.coupon}


class ShippingAddressSerializer(serializers.ModelSerializer):
  fullName = serializers.CharField(source="full_name")

  class Meta:
    model = ShippingAddress
    fields = ["fullName", "phone", "email", "pincode", "address1", "address2", "city", "state"]


class OrderItemSerializer(serializers.ModelSerializer):
  productId = serializers.IntegerField(source="product_id", read_only=True)
  variantKey = serializers.CharField(source="variant_sku", read_only=True)

  class Meta:
    model = OrderItem
    fields = ["productId", "variantKey", "qty", "product_name", "unit_price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
  id = serializers.UUIDField(source="public_id", read_only=True)
  placedAt = serializers.DateTimeField(source="created_at", read_only=True)
  method = serializers.CharField(source="payment_method", read_only=True)
  status = serializers.CharField(source="payment_status", read_only=True)
  fulfillment = serializers.CharField(source="fulfillment_status", read_only=True)
  shipping = ShippingAddressSerializer(source="shipping_address", read_only=True)
  items = OrderItemSerializer(many=True, read_only=True)
  totals = serializers.SerializerMethodField()

  class Meta:
    model = Order
    fields = ["id", "placedAt", "method", "status", "fulfillment", "shipping", "items", "totals"]

  def get_totals(self, obj: Order):
    return {
      "subtotal": obj.subtotal,
      "discount": obj.discount,
      "shipping": obj.shipping_fee,
      "total": obj.total,
      "coupon": obj.coupon_code or None,
    }


class OrderListSerializer(serializers.ModelSerializer):
  id = serializers.UUIDField(source="public_id", read_only=True)
  placedAt = serializers.DateTimeField(source="created_at", read_only=True)
  method = serializers.CharField(source="payment_method", read_only=True)
  status = serializers.CharField(source="payment_status", read_only=True)
  fulfillment = serializers.CharField(source="fulfillment_status", read_only=True)
  total = serializers.IntegerField(read_only=True)
  itemsCount = serializers.SerializerMethodField()

  class Meta:
    model = Order
    fields = ["id", "placedAt", "method", "status", "fulfillment", "total", "itemsCount"]

  def get_itemsCount(self, obj: Order):
    return sum(int(i.qty or 0) for i in obj.items.all())
