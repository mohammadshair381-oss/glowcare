import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views import View

from apps.catalog.models import MediaAsset
from apps.catalog.media_services import create_media_asset, media_asset_usage
from apps.cms.models import (
  AnnouncementBar,
  AppBanner,
  FeaturedLogo,
  FooterColumn,
  FooterLink,
  FooterSetting,
  FooterSocialLink,
  HeroSlide,
  Homepage,
  HomepageSection,
  NavigationLink,
  NavigationMenu,
  ProductSection,
  PromoStrip,
  Testimonial,
  ThemeSetting,
)


class StaffOnlyMixin(UserPassesTestMixin):
  def test_func(self):
    u = self.request.user
    return bool(u and u.is_authenticated and u.is_staff)


def _home() -> Homepage:
  home = Homepage.objects.filter(is_active=True).order_by("-updated_at").first()
  if home:
    return home
  return Homepage.objects.create(name="Homepage", is_active=True)


def _json(body: bytes):
  try:
    return json.loads(body.decode("utf-8") or "{}")
  except Exception:
    return {}


class EditorStateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def get(self, request: HttpRequest):
    home = _home()
    theme = home.theme or ThemeSetting.objects.filter(is_active=True).order_by("-updated_at").first()
    bar = home.announcement or AnnouncementBar.objects.order_by("-updated_at").first()
    menu = home.menu or NavigationMenu.objects.filter(is_active=True).order_by("-updated_at").first()
    footer = home.footer or FooterSetting.objects.order_by("-updated_at").first()

    promo = PromoStrip.objects.filter(homepage=home).order_by("sort_order", "id").first()
    appb = AppBanner.objects.filter(homepage=home).order_by("sort_order", "id").first()

    sections = list(home.sections.all().order_by("sort_order", "id"))
    hero_slides = list(home.hero_slides.all().order_by("sort_order", "id"))

    nav_links = list(menu.links.all().order_by("sort_order", "id")) if menu else []
    footer_cols = list(footer.columns.all().order_by("sort_order", "id")) if footer else []

    footer_payload = None
    if footer:
      footer_payload = {
        "id": footer.id,
        "aboutText": footer.about_text,
        "chips": footer.chips or [],
        "bottomLeft": footer.bottom_left,
        "bottomRight": footer.bottom_right,
        "columns": [],
      }
      for col in footer_cols:
        footer_payload["columns"].append(
          {
            "id": col.id,
            "title": col.title,
            "muted": col.muted,
            "sortOrder": col.sort_order,
            "links": [{"id": l.id, "label": l.label, "href": l.href, "sortOrder": l.sort_order} for l in col.links.all().order_by("sort_order", "id")],
            "social": [
              {"id": s.id, "label": s.label, "href": s.href, "aria": s.aria_label or "", "sortOrder": s.sort_order}
              for s in col.social_links.all().order_by("sort_order", "id")
            ],
          }
        )

    state = {
      "homepageId": home.id,
      "theme": {"id": theme.id if theme else None, "tokens": theme.tokens if theme else {}},
      "announcement": {
        "id": bar.id if bar else None,
        "enabled": bool(bar.enabled) if bar else False,
        "badge": bar.badge if bar else "",
        "text": bar.text if bar else "",
        "ctaText": bar.cta_text if bar else "",
        "ctaHref": bar.cta_href if bar else "",
        "bg": bar.bg if bar else "",
        "startAt": bar.start_at.isoformat() if bar and bar.start_at else "",
        "endAt": bar.end_at.isoformat() if bar and bar.end_at else "",
      },
      "navigation": {
        "menuId": menu.id if menu else None,
        "links": [
          {
            "id": l.id,
            "label": l.label,
            "href": l.href,
            "isPill": bool(l.is_pill),
            "enabled": bool(l.is_enabled),
            "sortOrder": l.sort_order,
          }
          for l in nav_links
        ],
      },
      "footer": footer_payload,
      "sections": [
        {
          "sectionId": s.section_id,
          "enabled": bool(s.enabled),
          "title": s.title,
          "sortOrder": s.sort_order,
          "settings": s.settings or {},
        }
        for s in sections
      ],
      "hero": {
        "autoplayMs": int(next(((s.settings or {}).get("autoplayMs", 5200) for s in sections if s.section_id == "hero"), 5200)),
        "slides": [
          {
            "id": hs.id,
            "enabled": bool(hs.enabled),
            "sortOrder": hs.sort_order,
            "kicker": hs.kicker,
            "headline": hs.headline,
            "headline2": hs.headline2,
            "sub": hs.sub,
            "primaryLabel": hs.primary_label,
            "primaryHref": hs.primary_href,
            "secondaryLabel": hs.secondary_label,
            "secondaryHref": hs.secondary_href,
            "overlayBg": hs.overlay_bg,
            "buttonStyles": hs.button_styles or {},
            "background": {"id": hs.background_id, "url": hs.background.file.url if hs.background_id else "", "kind": hs.background.kind if hs.background_id else ""},
            "cardA": {"id": hs.card_a_id, "url": hs.card_a.file.url if hs.card_a_id else ""},
            "cardB": {"id": hs.card_b_id, "url": hs.card_b.file.url if hs.card_b_id else ""},
            "cardC": {"id": hs.card_c_id, "url": hs.card_c.file.url if hs.card_c_id else ""},
            "ribbons": hs.ribbons or [],
            "meta": hs.meta or [],
          }
          for hs in hero_slides
        ],
      },
      "promoStrip": {
        "id": promo.id if promo else None,
        "enabled": bool(promo.enabled) if promo else False,
        "title": promo.title if promo else "",
        "subtitle": promo.subtitle if promo else "",
        "pills": promo.pills if promo else [],
        "buttonLabel": promo.button_label if promo else "",
        "buttonHref": promo.button_href if promo else "",
        "bg": promo.bg if promo else "",
        "startAt": promo.start_at.isoformat() if promo and promo.start_at else "",
        "endAt": promo.end_at.isoformat() if promo and promo.end_at else "",
      },
      "appBanner": {
        "id": appb.id if appb else None,
        "enabled": bool(appb.enabled) if appb else False,
        "title": appb.title if appb else "",
        "subtitle": appb.subtitle if appb else "",
        "stores": appb.stores if appb else [],
        "bg": appb.bg if appb else "",
      },
      "testimonials": [
        {
          "id": t.id,
          "enabled": bool(t.enabled),
          "sortOrder": t.sort_order,
          "name": t.name,
          "meta": t.meta,
          "rating": float(t.rating),
          "text": t.text,
          "avatar": {"id": t.avatar_id, "url": t.avatar.file.url if t.avatar_id else ""},
        }
        for t in Testimonial.objects.filter(homepage=home).order_by("sort_order", "id")
      ],
      "logos": [
        {"id": l.id, "enabled": bool(l.enabled), "sortOrder": l.sort_order, "name": l.name, "logo": {"id": l.logo_id, "url": l.logo.file.url if l.logo_id else ""}}
        for l in FeaturedLogo.objects.filter(homepage=home).order_by("sort_order", "id")
      ],
      "productSections": [
        {"id": ps.id, "kind": ps.kind, "enabled": bool(ps.enabled), "title": ps.title, "subtitle": ps.subtitle, "viewAllHref": ps.view_all_href, "tabs": ps.tabs or []}
        for ps in ProductSection.objects.filter(homepage=home).order_by("sort_order", "id")
      ],
    }
    return JsonResponse(state)


class HomepageApplyView(LoginRequiredMixin, StaffOnlyMixin, View):
  """
  Apply editor changes in one call.
  The payload is a "state diff" object; backend updates the corresponding models.
  """

  def post(self, request: HttpRequest):
    data = _json(request.body)
    home = _home()

    with transaction.atomic():
      # Theme
      theme_tokens = data.get("themeTokens")
      if isinstance(theme_tokens, dict):
        theme = home.theme or ThemeSetting.objects.filter(is_active=True).order_by("-updated_at").first()
        if not theme:
          theme = ThemeSetting.objects.create(name="Default", is_active=True, tokens={})
        theme.tokens = theme_tokens
        theme.save()
        home.theme = theme
        home.save(update_fields=["theme", "updated_at"])

      # Announcement
      ann = data.get("announcement")
      if isinstance(ann, dict):
        bar = home.announcement or AnnouncementBar.objects.order_by("-updated_at").first() or AnnouncementBar.objects.create(name="Primary")
        bar.enabled = bool(ann.get("enabled", bar.enabled))
        bar.badge = str(ann.get("badge", bar.badge or ""))[:40]
        bar.text = str(ann.get("text", bar.text or ""))[:160]
        bar.cta_text = str(ann.get("ctaText", bar.cta_text or ""))[:40]
        bar.cta_href = str(ann.get("ctaHref", bar.cta_href or ""))[:240]
        bar.bg = str(ann.get("bg", bar.bg or ""))[:160]
        for k, field in [("startAt", "start_at"), ("endAt", "end_at")]:
          raw = ann.get(k) or ""
          if raw:
            try:
              setattr(bar, field, timezone.datetime.fromisoformat(raw))
            except Exception:
              pass
          else:
            setattr(bar, field, None)
        bar.save()
        home.announcement = bar
        home.save(update_fields=["announcement", "updated_at"])

      # Sections (order/title/enabled/settings)
      sections = data.get("sections")
      if isinstance(sections, list):
        for idx, s in enumerate(sections):
          if not isinstance(s, dict):
            continue
          sid = str(s.get("sectionId") or "")
          if not sid:
            continue
          obj, _ = HomepageSection.objects.get_or_create(homepage=home, section_id=sid, defaults={"sort_order": idx})
          obj.sort_order = idx
          obj.enabled = bool(s.get("enabled", obj.enabled))
          obj.title = str(s.get("title", obj.title or ""))[:80]
          st = s.get("settings")
          if isinstance(st, dict):
            obj.settings = st
          obj.save()

      # Promo
      promo = data.get("promoStrip")
      if isinstance(promo, dict):
        obj = PromoStrip.objects.filter(homepage=home).order_by("sort_order", "id").first() or PromoStrip.objects.create(homepage=home, enabled=True, sort_order=0, title="Promo")
        obj.enabled = bool(promo.get("enabled", obj.enabled))
        obj.title = str(promo.get("title", obj.title or ""))[:70]
        obj.subtitle = str(promo.get("subtitle", obj.subtitle or ""))[:160]
        pills = promo.get("pills")
        if isinstance(pills, list):
          obj.pills = [str(x)[:60] for x in pills if str(x).strip()][:12]
        obj.button_label = str(promo.get("buttonLabel", obj.button_label or ""))[:30]
        obj.button_href = str(promo.get("buttonHref", obj.button_href or ""))[:240]
        obj.bg = str(promo.get("bg", obj.bg or ""))[:220]
        for k, field in [("startAt", "start_at"), ("endAt", "end_at")]:
          raw = promo.get(k) or ""
          if raw:
            try:
              setattr(obj, field, timezone.datetime.fromisoformat(raw))
            except Exception:
              pass
          else:
            setattr(obj, field, None)
        obj.save()

      # App banner
      appb = data.get("appBanner")
      if isinstance(appb, dict):
        obj = AppBanner.objects.filter(homepage=home).order_by("sort_order", "id").first() or AppBanner.objects.create(homepage=home, enabled=True, sort_order=0, title="Download app")
        obj.enabled = bool(appb.get("enabled", obj.enabled))
        obj.title = str(appb.get("title", obj.title or ""))[:70]
        obj.subtitle = str(appb.get("subtitle", obj.subtitle or ""))[:180]
        stores = appb.get("stores")
        if isinstance(stores, list):
          obj.stores = stores
        obj.bg = str(appb.get("bg", obj.bg or ""))[:220]
        obj.save()

      # Navigation
      nav = data.get("navigation")
      if isinstance(nav, dict) and isinstance(nav.get("links"), list):
        menu = home.menu or NavigationMenu.objects.filter(is_active=True).order_by("-updated_at").first() or NavigationMenu.objects.create(name="Primary", is_active=True)
        home.menu = menu
        home.save(update_fields=["menu", "updated_at"])
        menu.links.all().delete()
        for idx, l in enumerate(nav["links"][:32]):
          if not isinstance(l, dict):
            continue
          NavigationLink.objects.create(
            menu=menu,
            label=str(l.get("label") or "")[:40],
            href=str(l.get("href") or "")[:240],
            is_pill=bool(l.get("pill", False)),
            is_enabled=bool(l.get("enabled", True)),
            sort_order=idx,
          )

      # Footer
      footer = data.get("footer")
      if isinstance(footer, dict):
        f = home.footer or FooterSetting.objects.order_by("-updated_at").first() or FooterSetting.objects.create(name="Default")
        f.about_text = str(footer.get("aboutText") or "")[:1000]
        chips = footer.get("chips") or []
        if isinstance(chips, list):
          f.chips = [str(x)[:60] for x in chips if str(x).strip()][:12]
        f.bottom_left = str(footer.get("bottomLeft") or "")[:140]
        f.bottom_right = str(footer.get("bottomRight") or "")[:140]
        f.save()
        home.footer = f
        home.save(update_fields=["footer", "updated_at"])
        # rebuild cols/links/social
        f.columns.all().delete()
        cols = footer.get("columns") or []
        if isinstance(cols, list):
          for cidx, col in enumerate(cols[:6]):
            if not isinstance(col, dict):
              continue
            col_obj = FooterColumn.objects.create(footer=f, title=str(col.get("title") or "")[:50], muted=str(col.get("muted") or "")[:120], sort_order=cidx)
            links = col.get("links") or []
            if isinstance(links, list):
              for lidx, link in enumerate(links[:12]):
                if not isinstance(link, dict):
                  continue
                FooterLink.objects.create(column=col_obj, label=str(link.get("label") or "")[:80], href=str(link.get("href") or "")[:240], sort_order=lidx)
            socials = col.get("social") or []
            if isinstance(socials, list):
              for sidx, sl in enumerate(socials[:8]):
                if not isinstance(sl, dict):
                  continue
                FooterSocialLink.objects.create(column=col_obj, label=str(sl.get("label") or "")[:10], href=str(sl.get("href") or "")[:240], aria_label=str(sl.get("aria") or "")[:60], sort_order=sidx)

    return JsonResponse({"ok": True})


class MediaListCreateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def get(self, request: HttpRequest):
    items = []
    for a in MediaAsset.objects.order_by("-created_at")[:200]:
      items.append({"id": a.id, "kind": a.kind, "title": a.title, "alt": a.alt, "url": a.file.url})
    return JsonResponse({"items": items})

  def post(self, request: HttpRequest):
    f = request.FILES.get("file")
    if not f:
      return JsonResponse({"ok": False, "error": "missing_file"}, status=400)
    kind = request.POST.get("kind") or "image"
    title = (request.POST.get("title") or "")[:120]
    alt = (request.POST.get("alt") or "")[:180]
    a, _, _ = create_media_asset(file=f, kind=kind, title=title, alt=alt, context=MediaAsset.Context.CMS_SECTIONS, cms_section="visual_editor")
    return JsonResponse({"ok": True, "item": {"id": a.id, "kind": a.kind, "title": a.title, "alt": a.alt, "url": a.file.url}})


class MediaDeleteView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    a = MediaAsset.objects.filter(pk=pk).first()
    if not a:
      return JsonResponse({"ok": False}, status=404)
    usage = media_asset_usage(a)
    if usage.get("total_links", 0) > 0:
      return JsonResponse({"ok": False, "error": "in_use", "usage": usage}, status=409)
    a.delete()
    return JsonResponse({"ok": True})


class HeroSlideCreateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest):
    home = _home()
    slide = HeroSlide.objects.create(homepage=home, enabled=True, sort_order=HeroSlide.objects.filter(homepage=home).count())
    return JsonResponse({"ok": True, "id": slide.id})


class HeroSlideUpdateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    slide = HeroSlide.objects.filter(pk=pk).first()
    if not slide:
      return JsonResponse({"ok": False}, status=404)
    data = _json(request.body)
    # update simple fields
    for f, mx in [
      ("kicker", 90),
      ("headline", 40),
      ("headline2", 40),
      ("sub", 220),
      ("primaryLabel", 30),
      ("primaryHref", 240),
      ("secondaryLabel", 30),
      ("secondaryHref", 240),
      ("overlayBg", 220),
    ]:
      if f in data:
        val = str(data.get(f) or "")[:mx]
        if f == "primaryLabel":
          slide.primary_label = val
        elif f == "primaryHref":
          slide.primary_href = val
        elif f == "secondaryLabel":
          slide.secondary_label = val
        elif f == "secondaryHref":
          slide.secondary_href = val
        elif f == "overlayBg":
          slide.overlay_bg = val
        else:
          setattr(slide, f.lower() if f not in ["headline2"] else "headline2", val)
    if "enabled" in data:
      slide.enabled = bool(data.get("enabled"))
    if "sortOrder" in data:
      try:
        slide.sort_order = int(data.get("sortOrder"))
      except Exception:
        pass
    if "buttonStyles" in data and isinstance(data["buttonStyles"], dict):
      slide.button_styles = data["buttonStyles"]
    if "ribbons" in data and isinstance(data["ribbons"], list):
      slide.ribbons = data["ribbons"]
    if "meta" in data and isinstance(data["meta"], list):
      slide.meta = data["meta"]
    # media ids
    for key, field in [("backgroundId", "background_id"), ("cardAId", "card_a_id"), ("cardBId", "card_b_id"), ("cardCId", "card_c_id")]:
      if key in data:
        val = data.get(key)
        setattr(slide, field, int(val) if str(val).isdigit() else None)
    slide.save()
    return JsonResponse({"ok": True})


class HeroSlideDeleteViewApi(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    slide = HeroSlide.objects.filter(pk=pk).first()
    if not slide:
      return JsonResponse({"ok": False}, status=404)
    slide.delete()
    return JsonResponse({"ok": True})


class TestimonialCreateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest):
    home = _home()
    t = Testimonial.objects.create(
      homepage=home,
      enabled=True,
      sort_order=Testimonial.objects.filter(homepage=home).count(),
      name="Customer",
      meta="Verified buyer",
      rating=5,
      text="",
    )
    return JsonResponse({"ok": True, "id": t.id})


class TestimonialUpdateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    t = Testimonial.objects.filter(pk=pk).first()
    if not t:
      return JsonResponse({"ok": False}, status=404)
    data = _json(request.body)
    for f, mx in [("name", 60), ("meta", 80), ("text", 1600)]:
      if f in data:
        setattr(t, f, str(data.get(f) or "")[:mx])
    if "enabled" in data:
      t.enabled = bool(data.get("enabled"))
    if "sortOrder" in data:
      try:
        t.sort_order = int(data.get("sortOrder"))
      except Exception:
        pass
    if "rating" in data:
      try:
        t.rating = max(0, min(5, float(data.get("rating"))))
      except Exception:
        pass
    if "avatarId" in data:
      val = data.get("avatarId")
      t.avatar_id = int(val) if str(val).isdigit() else None
    t.save()
    return JsonResponse({"ok": True})


class TestimonialDeleteViewApi(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    t = Testimonial.objects.filter(pk=pk).first()
    if not t:
      return JsonResponse({"ok": False}, status=404)
    t.delete()
    return JsonResponse({"ok": True})


class FeaturedLogoCreateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest):
    home = _home()
    l = FeaturedLogo.objects.create(
      homepage=home,
      enabled=True,
      sort_order=FeaturedLogo.objects.filter(homepage=home).count(),
      name="Media",
    )
    return JsonResponse({"ok": True, "id": l.id})


class FeaturedLogoUpdateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    l = FeaturedLogo.objects.filter(pk=pk).first()
    if not l:
      return JsonResponse({"ok": False}, status=404)
    data = _json(request.body)
    if "name" in data:
      l.name = str(data.get("name") or "")[:40]
    if "enabled" in data:
      l.enabled = bool(data.get("enabled"))
    if "sortOrder" in data:
      try:
        l.sort_order = int(data.get("sortOrder"))
      except Exception:
        pass
    if "logoId" in data:
      val = data.get("logoId")
      l.logo_id = int(val) if str(val).isdigit() else None
    l.save()
    return JsonResponse({"ok": True})


class FeaturedLogoDeleteViewApi(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    l = FeaturedLogo.objects.filter(pk=pk).first()
    if not l:
      return JsonResponse({"ok": False}, status=404)
    l.delete()
    return JsonResponse({"ok": True})


class ProductSectionUpdateView(LoginRequiredMixin, StaffOnlyMixin, View):
  def post(self, request: HttpRequest, pk: int):
    ps = ProductSection.objects.filter(pk=pk).first()
    if not ps:
      return JsonResponse({"ok": False}, status=404)
    data = _json(request.body)
    if "enabled" in data:
      ps.enabled = bool(data.get("enabled"))
    if "title" in data:
      ps.title = str(data.get("title") or "")[:60]
    if "subtitle" in data:
      ps.subtitle = str(data.get("subtitle") or "")[:160]
    if "viewAllHref" in data:
      ps.view_all_href = str(data.get("viewAllHref") or "")[:240]
    if "sortOrder" in data:
      try:
        ps.sort_order = int(data.get("sortOrder"))
      except Exception:
        pass
    if "tabs" in data and isinstance(data.get("tabs"), list):
      ps.tabs = data.get("tabs")[:12]
    ps.save()
    return JsonResponse({"ok": True})
