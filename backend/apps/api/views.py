from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.cms.models import (
  AnnouncementBar,
  AppBanner,
  FeaturedLogo,
  FooterColumn,
  FooterSetting,
  HeroSlide,
  Homepage,
  NavigationMenu,
  ProductSection,
  PromoStrip,
  Testimonial,
  ThemeSetting,
)

from apps.customers.cart_service import (
  add_item,
  clear as clear_cart,
  get_or_create_cart_for_request,
  remove_item,
  set_coupon,
  set_item_qty,
)
from apps.customers.order_service import create_order_from_cart, validate_shipping

from .serializers import CartSerializer, OrderListSerializer, OrderSerializer, ProductSerializer


def _active_homepage() -> Homepage | None:
  return Homepage.objects.filter(is_active=True).order_by("-updated_at").first()


def _theme_payload(theme: ThemeSetting | None):
  return theme.tokens if theme else {}


def _nav_payload(menu: NavigationMenu | None):
  if not menu:
    return {"links": []}
  links = menu.links.filter(is_enabled=True).order_by("sort_order", "id")
  return {
    "links": [{"label": l.label, "href": l.href, "pill": bool(l.is_pill)} for l in links],
  }


def _footer_payload(footer: FooterSetting | None):
  if not footer:
    return None
  cols = []
  for col in footer.columns.all().order_by("sort_order", "id"):
    cols.append(
      {
        "title": col.title,
        "muted": col.muted,
        "links": [{"label": l.label, "href": l.href} for l in col.links.all().order_by("sort_order", "id")],
        "social": [
          {"label": s.label, "href": s.href, "aria": s.aria_label or s.label} for s in col.social_links.all().order_by("sort_order", "id")
        ],
      }
    )
  return {
    "aboutText": footer.about_text,
    "chips": footer.chips or [],
    "columns": cols,
    "bottomLeft": footer.bottom_left,
    "bottomRight": footer.bottom_right,
  }


def _announcement_payload(bar: AnnouncementBar | None):
  if not bar:
    return {"enabled": False}
  now = timezone.now()
  enabled = bar.is_visible_now(now)
  payload = {
    "enabled": enabled,
    "badge": bar.badge,
    "text": bar.text,
    "ctaText": bar.cta_text,
    "ctaHref": bar.cta_href,
  }
  if bar.bg:
    payload["bg"] = bar.bg
  return payload


class HomepageView(APIView):
  """
  Returns a single JSON payload used by the premium frontend to render the homepage.
  This is the "Shopify customizer / Elementor" style data contract.
  """

  def get(self, request):
    home = _active_homepage()
    if not home:
      return Response({"detail": "Homepage not configured"}, status=404)

    sections = [
      {"id": s.section_id, "enabled": s.enabled, "title": s.title or "", "settings": (s.settings or {})}
      for s in home.sections.all().order_by("sort_order", "id")
    ]

    hero_autoplay_ms = 5200
    hero_section = next((s for s in home.sections.all() if s.section_id == "hero"), None)
    if hero_section and hero_section.settings:
      hero_autoplay_ms = int(hero_section.settings.get("autoplayMs", hero_autoplay_ms))

    slides = []
    for s in HeroSlide.objects.filter(homepage=home, enabled=True).order_by("sort_order", "id"):
      slides.append(
        {
          "kicker": s.kicker,
          "headline": s.headline,
          "headline2": s.headline2,
          "sub": s.sub,
          "primary": {"label": s.primary_label, "href": s.primary_href},
          "secondary": {"label": s.secondary_label, "href": s.secondary_href},
          "cards": [
            s.card_a.file.url if s.card_a_id else "",
            s.card_b.file.url if s.card_b_id else "",
            s.card_c.file.url if s.card_c_id else "",
          ],
          "background": {"kind": (s.background.kind if s.background_id else ""), "url": (s.background.file.url if s.background_id else "")},
          "overlayBg": s.overlay_bg or "",
          "buttonStyles": s.button_styles or {},
          "ribbons": s.ribbons or [],
          "meta": s.meta or [],
        }
      )

    now = timezone.now()
    promo = (
      PromoStrip.objects.filter(homepage=home, enabled=True)
      .order_by("sort_order", "id")
      .first()
    )
    promo_payload = None
    if promo and (not promo.start_at or promo.start_at <= now) and (not promo.end_at or promo.end_at >= now):
      promo_payload = {
        "title": promo.title,
        "subtitle": promo.subtitle,
        "pills": promo.pills or [],
        "button": {"label": promo.button_label, "href": promo.button_href},
        "bg": promo.bg or "",
      }

    app_banner = AppBanner.objects.filter(homepage=home, enabled=True).order_by("sort_order", "id").first()
    app_payload = None
    if app_banner:
      app_payload = {"title": app_banner.title, "subtitle": app_banner.subtitle, "stores": app_banner.stores or [], "bg": app_banner.bg or ""}

    logos = [{"name": l.name, "logo": (l.logo.file.url if l.logo_id else "")} for l in FeaturedLogo.objects.filter(homepage=home, enabled=True).order_by("sort_order", "id")]

    testimonials = []
    for t in Testimonial.objects.filter(homepage=home, enabled=True).order_by("sort_order", "id"):
      testimonials.append(
        {
          "name": t.name,
          "meta": t.meta,
          "rating": float(t.rating),
          "text": t.text,
          "avatar": t.avatar.file.url if t.avatar_id else "",
        }
      )

    product_sections = {}
    for ps in ProductSection.objects.filter(homepage=home, enabled=True).order_by("sort_order", "id"):
      product_sections[ps.kind] = {
        "title": ps.title,
        "subtitle": ps.subtitle,
        "viewAllHref": ps.view_all_href,
        "tabs": ps.tabs or [],
      }

    payload = {
      "version": 1,
      "theme": _theme_payload(home.theme),
      "announcement": _announcement_payload(home.announcement),
      "navigation": _nav_payload(home.menu),
      "footer": _footer_payload(home.footer),
      "sections": sections,
      "hero": {"autoplayMs": hero_autoplay_ms, "slides": slides},
      "promoStrip": promo_payload,
      "appBanner": app_payload,
      "logos": {"items": [l["name"] for l in logos], "media": logos},
      "testimonials": {"items": testimonials},
      "productSections": product_sections,
      # Additional keys can be added without breaking frontend
    }

    return Response(payload)


class ProductListView(generics.ListAPIView):
  queryset = Product.objects.filter(is_active=True, is_published=True).select_related("category", "primary_media").prefetch_related("variants", "images__media")
  serializer_class = ProductSerializer
  filterset_fields = ["badge", "category__slug", "brand"]
  ordering_fields = ["price", "rating", "updated_at"]


class ProductDetailView(generics.RetrieveAPIView):
  queryset = Product.objects.filter(is_active=True, is_published=True).select_related("category", "primary_media").prefetch_related("variants", "images__media")
  serializer_class = ProductSerializer


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfCookieView(APIView):
  permission_classes = [permissions.AllowAny]

  def get(self, request):
    return Response({"detail": "ok"})


class CartView(APIView):
  permission_classes = [permissions.AllowAny]

  def get(self, request):
    cart = get_or_create_cart_for_request(request)
    cart = (
      cart.__class__.objects.filter(pk=cart.pk)
      .prefetch_related("items__product__variants", "items__product__images__media")
      .select_related("user")
      .first()
    )
    return Response(CartSerializer(cart).data)


class CartItemAddView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    cart = get_or_create_cart_for_request(request)
    product_id = request.data.get("productId") or request.data.get("product_id")
    variant_key = request.data.get("variantKey") or request.data.get("variant_sku") or ""
    qty = request.data.get("qty") or 1
    try:
      product_id_int = int(product_id)
    except Exception:
      return Response({"detail": "product_not_found"}, status=status.HTTP_400_BAD_REQUEST)
    try:
      add_item(cart, product_id_int, str(variant_key), int(qty))
    except ValueError as e:
      return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    cart.refresh_from_db()
    cart = cart.__class__.objects.filter(pk=cart.pk).prefetch_related("items__product__variants", "items__product__images__media").first()
    return Response(CartSerializer(cart).data, status=201)


class CartItemQtyView(APIView):
  permission_classes = [permissions.AllowAny]

  def patch(self, request, item_id: int):
    cart = get_or_create_cart_for_request(request)
    qty = request.data.get("qty") or 1
    try:
      set_item_qty(cart, int(item_id), int(qty))
    except Exception:
      return Response({"detail": "invalid_item"}, status=status.HTTP_400_BAD_REQUEST)
    cart.refresh_from_db()
    cart = cart.__class__.objects.filter(pk=cart.pk).prefetch_related("items__product__variants", "items__product__images__media").first()
    return Response(CartSerializer(cart).data)


class CartItemDeleteView(APIView):
  permission_classes = [permissions.AllowAny]

  def delete(self, request, item_id: int):
    cart = get_or_create_cart_for_request(request)
    remove_item(cart, int(item_id))
    cart.refresh_from_db()
    cart = cart.__class__.objects.filter(pk=cart.pk).prefetch_related("items__product__variants", "items__product__images__media").first()
    return Response(CartSerializer(cart).data)


class CartClearView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    cart = get_or_create_cart_for_request(request)
    clear_cart(cart)
    cart.refresh_from_db()
    cart = cart.__class__.objects.filter(pk=cart.pk).prefetch_related("items__product__variants", "items__product__images__media").first()
    return Response(CartSerializer(cart).data)


class CartCouponView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request):
    cart = get_or_create_cart_for_request(request)
    code = request.data.get("code") or ""
    set_coupon(cart, str(code))
    cart.refresh_from_db()
    cart = cart.__class__.objects.filter(pk=cart.pk).prefetch_related("items__product__variants", "items__product__images__media").first()
    return Response(CartSerializer(cart).data)


class CheckoutShippingView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def get(self, request):
    return Response({"shipping": request.session.get("checkout_shipping")})

  def post(self, request):
    try:
      shipping = validate_shipping(request.data or {})
    except ValueError as e:
      payload = e.args[0]
      if isinstance(payload, dict):
        return Response({"errors": payload}, status=status.HTTP_400_BAD_REQUEST)
      return Response({"detail": "invalid_shipping"}, status=status.HTTP_400_BAD_REQUEST)

    request.session["checkout_shipping"] = {
      "fullName": shipping.fullName,
      "phone": shipping.phone,
      "email": shipping.email,
      "pincode": shipping.pincode,
      "address1": shipping.address1,
      "address2": shipping.address2,
      "city": shipping.city,
      "state": shipping.state,
    }
    request.session.modified = True
    return Response({"ok": True})


class CheckoutPlaceView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request):
    cart = get_or_create_cart_for_request(request)
    shipping_raw = request.session.get("checkout_shipping") or None
    if not shipping_raw:
      return Response({"detail": "missing_shipping"}, status=status.HTTP_400_BAD_REQUEST)
    try:
      shipping = validate_shipping(shipping_raw)
    except ValueError:
      return Response({"detail": "invalid_shipping"}, status=status.HTTP_400_BAD_REQUEST)

    method = str(request.data.get("method") or "upi").lower()
    mark_paid = bool(request.data.get("markPaid") or False)
    if method not in {"upi", "card", "cod"}:
      return Response({"detail": "invalid_method"}, status=status.HTTP_400_BAD_REQUEST)

    try:
      order = create_order_from_cart(cart=cart, user=request.user, shipping=shipping, payment_method=method, mark_paid=mark_paid)
    except ValueError as e:
      return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Clear shipping draft after successful placement.
    if "checkout_shipping" in request.session:
      del request.session["checkout_shipping"]
      request.session.modified = True

    return Response({"orderId": str(order.public_id)})


class OrderListView(generics.ListAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = OrderListSerializer

  def get_queryset(self):
    return (
      self.request.user.orders.all()
      .prefetch_related("items")
      .order_by("-created_at")
    )


class OrderDetailView(generics.RetrieveAPIView):
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = OrderSerializer
  lookup_field = "public_id"
  lookup_url_kwarg = "order_id"

  def get_queryset(self):
    return self.request.user.orders.all().prefetch_related("items", "shipping_address")
