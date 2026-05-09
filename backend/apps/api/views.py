from django.utils import timezone
from rest_framework import generics
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

from .serializers import ProductSerializer


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
