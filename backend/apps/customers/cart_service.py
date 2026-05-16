from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest

from apps.catalog.models import Product, Variant

from .models import Cart, CartItem

User = get_user_model()


COUPONS: dict[str, dict[str, Any]] = {
  "GLOW10": {"code": "GLOW10", "type": "percent", "value": 10, "label": "10% OFF"},
  "FREESHIP": {"code": "FREESHIP", "type": "ship", "value": 0, "label": "Free shipping"},
}

SHIPPING_FREE_ABOVE = 499
SHIPPING_BASE = 49

MAX_QTY_PER_ITEM = 10


def _ensure_session_key(request: HttpRequest) -> str:
  if request.session.session_key:
    return request.session.session_key
  request.session.save()
  return request.session.session_key or ""


def get_or_create_cart_for_request(request: HttpRequest) -> Cart:
  if request.user.is_authenticated:
    cart, _ = Cart.objects.get_or_create(user=request.user, defaults={"coupon_code": ""})
    return cart
  session_key = _ensure_session_key(request)
  cart, _ = Cart.objects.get_or_create(session_key=session_key, defaults={"coupon_code": ""})
  return cart


@transaction.atomic
def merge_session_cart_to_user(request: HttpRequest) -> None:
  if not request.user.is_authenticated:
    return
  session_key = request.session.session_key
  if not session_key:
    return
  try:
    session_cart = Cart.objects.select_for_update().get(session_key=session_key, user__isnull=True)
  except Cart.DoesNotExist:
    return

  user_cart, _ = Cart.objects.select_for_update().get_or_create(user=request.user, defaults={"coupon_code": ""})
  if not user_cart.coupon_code and session_cart.coupon_code:
    user_cart.coupon_code = session_cart.coupon_code
    user_cart.save(update_fields=["coupon_code"])

  for it in session_cart.items.select_related("product").all():
    _add_or_increment(user_cart, it.product_id, it.variant_sku, it.qty)

  session_cart.delete()


def _variant_for(product: Product, variant_sku: str) -> Variant | None:
  sku = str(variant_sku or "").strip()
  if not sku:
    return None
  return product.variants.filter(sku=sku, is_active=True).first()


def _clamp_qty(qty: Any) -> int:
  try:
    q = int(qty)
  except Exception:
    q = 1
  q = max(1, min(MAX_QTY_PER_ITEM, q))
  return q


@transaction.atomic
def _add_or_increment(cart: Cart, product_id: int, variant_sku: str, qty: int) -> CartItem:
  cart = Cart.objects.select_for_update().get(pk=cart.pk)
  item, created = CartItem.objects.select_for_update().get_or_create(
    cart=cart,
    product_id=product_id,
    variant_sku=variant_sku,
    defaults={"qty": 0},
  )
  want = _clamp_qty(qty)
  next_qty = want if created else _clamp_qty(item.qty + want)
  item.qty = next_qty
  item.save(update_fields=["qty", "updated_at"])
  return item


@transaction.atomic
def add_item(cart: Cart, product_id: int, variant_sku: str, qty: int) -> CartItem:
  product = Product.objects.filter(pk=product_id, is_active=True, is_published=True).prefetch_related("variants").first()
  if not product:
    raise ValueError("product_not_found")
  variant = _variant_for(product, variant_sku)
  if not variant:
    raise ValueError("variant_not_found")
  if variant.stock <= 0:
    raise ValueError("out_of_stock")

  # Clamp to available stock.
  want = _clamp_qty(qty)
  existing = CartItem.objects.filter(cart=cart, product=product, variant_sku=variant.sku).first()
  current_qty = int(existing.qty) if existing else 0
  remaining = max(0, int(variant.stock) - current_qty)
  if remaining <= 0:
    raise ValueError("out_of_stock")
  qty_to_add = min(want, remaining)
  item = _add_or_increment(cart, product.id, variant.sku, qty_to_add)
  return item


@transaction.atomic
def set_item_qty(cart: Cart, item_id: int, qty: int) -> CartItem:
  cart = Cart.objects.select_for_update().get(pk=cart.pk)
  item = CartItem.objects.select_for_update().select_related("product").get(pk=item_id, cart=cart)
  variant = _variant_for(item.product, item.variant_sku)
  if not variant:
    raise ValueError("variant_not_found")
  safe = _clamp_qty(qty)
  safe = min(safe, max(1, int(variant.stock)))
  item.qty = safe
  item.save(update_fields=["qty", "updated_at"])
  return item


@transaction.atomic
def remove_item(cart: Cart, item_id: int) -> None:
  cart = Cart.objects.select_for_update().get(pk=cart.pk)
  CartItem.objects.filter(cart=cart, pk=item_id).delete()


@transaction.atomic
def clear(cart: Cart) -> None:
  cart = Cart.objects.select_for_update().get(pk=cart.pk)
  cart.items.all().delete()
  cart.coupon_code = ""
  cart.save(update_fields=["coupon_code", "updated_at"])


@transaction.atomic
def set_coupon(cart: Cart, code: str) -> str:
  cart = Cart.objects.select_for_update().get(pk=cart.pk)
  raw = str(code or "").strip().upper()
  cart.coupon_code = raw if raw in COUPONS else ""
  cart.save(update_fields=["coupon_code", "updated_at"])
  return cart.coupon_code


@dataclass(frozen=True)
class CartTotals:
  subtotal: int
  discount: int
  shipping: int
  total: int
  coupon: dict[str, Any] | None


def compute_totals(cart: Cart) -> CartTotals:
  items = cart.items.select_related("product").all()
  subtotal = 0
  for it in items:
    subtotal += int(it.product.price or 0) * int(it.qty or 0)

  coupon = COUPONS.get((cart.coupon_code or "").upper() or "", None)
  discount = 0
  if coupon and coupon.get("type") == "percent":
    discount = round(subtotal * int(coupon.get("value") or 0) / 100)

  shipping = 0 if (coupon and coupon.get("type") == "ship") else (0 if subtotal >= SHIPPING_FREE_ABOVE else SHIPPING_BASE)
  total = max(0, int(subtotal) - int(discount) + int(shipping))
  return CartTotals(subtotal=subtotal, discount=discount, shipping=shipping, total=total, coupon=coupon)

