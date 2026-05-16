from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db import transaction

from apps.catalog.models import Product

from .cart_service import compute_totals
from .models import Cart, Order, OrderItem, ShippingAddress


@dataclass(frozen=True)
class ShippingPayload:
  fullName: str
  phone: str
  email: str
  pincode: str
  address1: str
  address2: str
  city: str
  state: str


def _clean_str(v: Any, max_len: int) -> str:
  s = str(v or "").strip()
  if len(s) > max_len:
    s = s[:max_len]
  return s


def validate_shipping(data: dict[str, Any]) -> ShippingPayload:
  full_name = _clean_str(data.get("fullName"), 120)
  phone = _clean_str(data.get("phone"), 30)
  email = _clean_str(data.get("email"), 254)
  pincode = _clean_str(data.get("pincode"), 12)
  address1 = _clean_str(data.get("address1"), 220)
  address2 = _clean_str(data.get("address2"), 220)
  city = _clean_str(data.get("city"), 80)
  state = _clean_str(data.get("state"), 80)

  errors: dict[str, str] = {}
  if len(full_name) < 2:
    errors["fullName"] = "Enter full name"
  digits_phone = "".join([c for c in phone if c.isdigit()])
  if len(digits_phone) < 10:
    errors["phone"] = "Enter valid phone"
  digits_pin = "".join([c for c in pincode if c.isdigit()])
  if len(digits_pin) < 6:
    errors["pincode"] = "Enter pincode"
  if len(address1) < 5:
    errors["address1"] = "Enter address"
  if not city:
    errors["city"] = "Enter city"
  if not state:
    errors["state"] = "Enter state"

  if errors:
    raise ValueError(errors)

  return ShippingPayload(
    fullName=full_name,
    phone=phone,
    email=email,
    pincode=pincode,
    address1=address1,
    address2=address2,
    city=city,
    state=state,
  )


@transaction.atomic
def create_order_from_cart(*, cart: Cart, user, shipping: ShippingPayload, payment_method: str, mark_paid: bool) -> Order:
  if not user or not user.is_authenticated:
    raise ValueError("auth_required")

  cart = Cart.objects.select_for_update().get(pk=cart.pk)
  items = list(cart.items.select_related("product").all())
  if not items:
    raise ValueError("cart_empty")

  # Re-validate product/variant availability under lock.
  for it in items:
    product: Product = it.product
    if not (product.is_active and product.is_published):
      raise ValueError("product_unavailable")
    variant = product.variants.filter(sku=it.variant_sku, is_active=True).first()
    if not variant:
      raise ValueError("variant_not_found")
    if int(it.qty or 0) > int(variant.stock or 0):
      raise ValueError("out_of_stock")

  totals = compute_totals(cart)

  addr = ShippingAddress.objects.create(
    user=user,
    full_name=shipping.fullName,
    phone=shipping.phone,
    email=shipping.email,
    pincode=shipping.pincode,
    address1=shipping.address1,
    address2=shipping.address2,
    city=shipping.city,
    state=shipping.state,
  )

  order = Order.objects.create(
    user=user,
    payment_method=payment_method,
    payment_status=(Order.PaymentStatus.PAID if mark_paid else Order.PaymentStatus.UNPAID),
    fulfillment_status=Order.FulfillmentStatus.PLACED,
    shipping_address=addr,
    coupon_code=cart.coupon_code or "",
    subtotal=totals.subtotal,
    discount=totals.discount,
    shipping_fee=totals.shipping,
    total=totals.total,
    currency="INR",
  )

  order_items: list[OrderItem] = []
  for it in items:
    product: Product = it.product
    unit_price = int(product.price or 0)
    qty = int(it.qty or 0)
    order_items.append(
      OrderItem(
        order=order,
        product=product,
        variant_sku=it.variant_sku,
        qty=qty,
        product_name=product.name or "",
        unit_price=unit_price,
        line_total=unit_price * qty,
      )
    )
  OrderItem.objects.bulk_create(order_items)

  # Clear cart after successful order creation to prevent duplicates on refresh/retry.
  cart.items.all().delete()
  cart.coupon_code = ""
  cart.save(update_fields=["coupon_code", "updated_at"])

  return order
