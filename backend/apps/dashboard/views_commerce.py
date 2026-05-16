from __future__ import annotations

from datetime import timedelta
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from apps.catalog.models import Product, Variant
from apps.customers.models import Order, OrderItem, ShippingAddress

from .mixins import StaffRequiredMixin


def _qs_base(request: HttpRequest) -> str:
  qd = request.GET.copy()
  if "page" in qd:
    qd.pop("page", None)
  s = urlencode([(k, v) for k, vals in qd.lists() for v in vals if v is not None and v != ""])
  return f"&{s}" if s else ""


class OrdersListView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/orders.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)

    q = (self.request.GET.get("q") or "").strip()
    pay = (self.request.GET.get("payment") or "").strip().lower()
    full = (self.request.GET.get("fulfillment") or "").strip().lower()

    qs = (
      Order.objects.select_related("user", "shipping_address")
      .prefetch_related("items")
      .order_by("-created_at")
    )

    if q:
      qs = qs.filter(
        Q(public_id__icontains=q)
        | Q(user__username__icontains=q)
        | Q(user__email__icontains=q)
        | Q(shipping_address__full_name__icontains=q)
        | Q(shipping_address__phone__icontains=q)
      )
    if pay in {c[0] for c in Order.PaymentStatus.choices}:
      qs = qs.filter(payment_status=pay)
    if full in {c[0] for c in Order.FulfillmentStatus.choices}:
      qs = qs.filter(fulfillment_status=full)

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(self.request.GET.get("page") or 1)

    ctx.update(
      {
        "q": q,
        "payment": pay,
        "fulfillment": full,
        "orders": page_obj.object_list,
        "page_obj": page_obj,
        "qs_base": _qs_base(self.request),
        "payment_choices": Order.PaymentStatus.choices,
        "fulfillment_choices": Order.FulfillmentStatus.choices,
      }
    )
    return ctx


class OrderDetailView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/order_detail.html"

  def get(self, request: HttpRequest, order_id) -> HttpResponse:
    order = get_object_or_404(
      Order.objects.select_related("user", "shipping_address").prefetch_related("items__product"),
      public_id=order_id,
    )
    return render(
      request,
      self.template_name,
      {
        "order": order,
        "saved": (request.GET.get("saved") or "") == "1",
        "payment_choices": Order.PaymentStatus.choices,
        "fulfillment_choices": Order.FulfillmentStatus.choices,
      },
    )

  def post(self, request: HttpRequest, order_id) -> HttpResponse:
    order = get_object_or_404(Order, public_id=order_id)
    payment = (request.POST.get("payment_status") or "").strip().lower()
    fulfillment = (request.POST.get("fulfillment_status") or "").strip().lower()

    updates: dict[str, str] = {}
    if payment in {c[0] for c in Order.PaymentStatus.choices}:
      updates["payment_status"] = payment
    if fulfillment in {c[0] for c in Order.FulfillmentStatus.choices}:
      updates["fulfillment_status"] = fulfillment

    if updates:
      Order.objects.filter(pk=order.pk).update(**updates)
    return redirect(f"{reverse('dashboard:order_detail', kwargs={'order_id': order.public_id})}?saved=1")


class CustomersListView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/customers.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    User = get_user_model()

    q = (self.request.GET.get("q") or "").strip()
    qs = User.objects.all().order_by("-date_joined")
    if q:
      qs = qs.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))

    qs = qs.annotate(
      orders_count=Count("orders", distinct=True),
      total_spent=Sum("orders__total"),
      last_order_at=Max("orders__created_at"),
    )

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(self.request.GET.get("page") or 1)

    ctx.update({"q": q, "customers": page_obj.object_list, "page_obj": page_obj, "qs_base": _qs_base(self.request)})
    return ctx


class CustomerDetailView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/customer_detail.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    User = get_user_model()
    u = get_object_or_404(User, pk=kwargs.get("user_id"))

    orders = (
      Order.objects.filter(user=u)
      .select_related("shipping_address")
      .prefetch_related("items")
      .order_by("-created_at")[:50]
    )
    addresses = ShippingAddress.objects.filter(user=u).order_by("-created_at")[:10]

    ctx.update({"customer": u, "orders": orders, "addresses": addresses})
    return ctx


class InventoryListView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/inventory.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)

    q = (self.request.GET.get("q") or "").strip()
    low = (self.request.GET.get("low") or "").strip()

    qs = Variant.objects.select_related("product").order_by("product__name", "id")
    if q:
      qs = qs.filter(Q(product__name__icontains=q) | Q(product__sku__icontains=q) | Q(sku__icontains=q) | Q(shade__icontains=q))
    if low == "1":
      qs = qs.filter(track_inventory=True, stock__lte=F("low_stock_threshold"))

    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(self.request.GET.get("page") or 1)

    low_ids = set(Variant.objects.filter(track_inventory=True, is_active=True, stock__lte=F("low_stock_threshold")).values_list("id", flat=True))

    ctx.update(
      {
        "q": q,
        "low": low,
        "variants": page_obj.object_list,
        "page_obj": page_obj,
        "qs_base": _qs_base(self.request),
        "low_variant_ids": low_ids,
      }
    )
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    vid = request.POST.get("variant_id") or ""
    if not str(vid).isdigit():
      return redirect("dashboard:inventory")

    v = Variant.objects.select_related("product").filter(pk=int(vid)).first()
    if not v:
      return redirect("dashboard:inventory")

    def _int(name: str, default: int):
      raw = request.POST.get(name)
      if raw is None:
        return default
      try:
        return max(0, int(raw))
      except Exception:
        return default

    v.stock = _int("stock", int(v.stock or 0))
    v.low_stock_threshold = _int("low_stock_threshold", int(v.low_stock_threshold or 0))
    v.track_inventory = bool(request.POST.get("track_inventory") == "on")
    v.is_active = bool(request.POST.get("is_active") == "on")
    v.save(update_fields=["stock", "low_stock_threshold", "track_inventory", "is_active", "updated_at"])

    return redirect(f"{request.path}?saved=1{_qs_base(request)}")


def dashboard_commerce_snapshot() -> dict:
  now = timezone.now()
  last_30 = now - timedelta(days=30)

  totals = Order.objects.aggregate(
    orders=Count("id"),
    revenue=Sum("total"),
  )

  recent_orders = (
    Order.objects.select_related("user")
    .order_by("-created_at")[:8]
  )

  User = get_user_model()
  recent_customers = (
    User.objects.annotate(last_order_at=Max("orders__created_at"))
    .filter(last_order_at__isnull=False)
    .order_by("-last_order_at")[:6]
  )

  low_stock = Variant.objects.filter(is_active=True, track_inventory=True, stock__lte=F("low_stock_threshold")).count()

  top_items = (
    OrderItem.objects.filter(order__created_at__gte=last_30)
    .values("product_id", "product_name")
    .annotate(qty=Sum("qty"), revenue=Sum("line_total"))
    .order_by("-revenue")[:6]
  )

  return {
    "totals": {
      "orders": int(totals.get("orders") or 0),
      "revenue": int(totals.get("revenue") or 0),
      "products": int(Product.objects.count()),
      "low_stock": int(low_stock),
    },
    "recent_orders": list(recent_orders),
    "recent_customers": list(recent_customers),
    "top_items": list(top_items),
  }
