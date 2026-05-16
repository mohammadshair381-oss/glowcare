import uuid

from django.conf import settings
from django.db import models

from apps.catalog.models import Product


class CustomerProfile(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile")

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return self.user.get_username()


class ShippingAddress(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shipping_addresses")

  full_name = models.CharField(max_length=120)
  phone = models.CharField(max_length=30)
  email = models.EmailField(blank=True, default="")
  pincode = models.CharField(max_length=12)
  address1 = models.CharField(max_length=220)
  address2 = models.CharField(max_length=220, blank=True, default="")
  city = models.CharField(max_length=80)
  state = models.CharField(max_length=80)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return f"{self.full_name} ({self.city})"


class Cart(models.Model):
  """
  A single active cart per user OR per anonymous session.
  Anonymous carts are keyed by session_key and can be merged on login.
  """

  user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="cart",
    null=True,
    blank=True,
  )
  session_key = models.CharField(max_length=64, unique=True, null=True, blank=True)

  coupon_code = models.CharField(max_length=20, blank=True, default="")

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return f"Cart({self.user_id or self.session_key or 'unknown'})"


class CartItem(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
  product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
  variant_sku = models.CharField(max_length=50)
  qty = models.PositiveSmallIntegerField(default=1)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    unique_together = [("cart", "product", "variant_sku")]

  def __str__(self) -> str:
    return f"{self.cart_id} {self.product_id} {self.variant_sku} x{self.qty}"


class Order(models.Model):
  class PaymentStatus(models.TextChoices):
    UNPAID = "unpaid", "Unpaid"
    PAID = "paid", "Paid"
    REFUNDED = "refunded", "Refunded"

  class FulfillmentStatus(models.TextChoices):
    PLACED = "placed", "Placed"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELED = "canceled", "Canceled"

  class PaymentMethod(models.TextChoices):
    UPI = "upi", "UPI"
    CARD = "card", "Card"
    COD = "cod", "COD"

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
  public_id = models.UUIDField(unique=True, db_index=True, default=uuid.uuid4, editable=False)

  payment_method = models.CharField(max_length=16, choices=PaymentMethod.choices, default=PaymentMethod.UPI)
  payment_status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
  fulfillment_status = models.CharField(max_length=16, choices=FulfillmentStatus.choices, default=FulfillmentStatus.PLACED)

  shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.PROTECT, related_name="orders")

  coupon_code = models.CharField(max_length=20, blank=True, default="")
  subtotal = models.PositiveIntegerField(default=0)
  discount = models.PositiveIntegerField(default=0)
  shipping_fee = models.PositiveIntegerField(default=0)
  total = models.PositiveIntegerField(default=0)
  currency = models.CharField(max_length=8, default="INR")

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return f"Order({self.public_id})"


class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
  product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
  variant_sku = models.CharField(max_length=50)
  qty = models.PositiveSmallIntegerField(default=1)

  product_name = models.CharField(max_length=180, blank=True, default="")
  unit_price = models.PositiveIntegerField(default=0)
  line_total = models.PositiveIntegerField(default=0)

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
    return f"{self.order_id} {self.product_id} x{self.qty}"
