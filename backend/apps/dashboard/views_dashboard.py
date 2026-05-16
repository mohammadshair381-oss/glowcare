from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import F, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.views import View
from django.views.generic import TemplateView

from django.core.files.base import ContentFile

from apps.catalog.models import Brand, Category, MediaAsset, Product, ProductImage, SubCategory, Variant
from apps.catalog.media_services import create_media_asset, media_asset_usage, search_assets_queryset
from apps.cms.models import (
  AnnouncementBar,
  AppBanner,
  FeaturedLogo,
  FooterColumn,
  FooterLink,
  FooterSocialLink,
  FooterSetting,
  HeroSlide,
  Homepage,
  HomepageSection,
  NavigationLink,
  NavigationMenu,
  PromoStrip,
  ProductSection,
  Testimonial,
  ThemeSetting,
)

from .forms import (
  AnnouncementForm,
  AppBannerForm,
  HeroSlideForm,
  ProductSectionForm,
  ProductForm,
  PromoStripForm,
  ThemeForm,
  VariantForm,
)


class StaffRequiredMixin(UserPassesTestMixin):
  def test_func(self):
    u = self.request.user
    return bool(u and u.is_authenticated and u.is_staff)

  def handle_no_permission(self):
    if not self.request.user.is_authenticated:
      return super().handle_no_permission()
    from django.contrib.auth import logout

    logout(self.request)
    return redirect("dashboard:login")


class DashboardHomeView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/home.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["counts"] = {
      "products": Product.objects.count(),
      "hero_slides": HeroSlide.objects.count(),
      "sections": HomepageSection.objects.count(),
    }
    return ctx


def _get_active_homepage() -> Homepage:
  home = Homepage.objects.filter(is_active=True).order_by("-updated_at").first()
  if home:
    return home
  # bootstrap if empty
  home = Homepage.objects.create(name="Homepage", is_active=True)
  HomepageSection.objects.bulk_create(
    [
      HomepageSection(homepage=home, section_id="hero", enabled=True, sort_order=0, settings={"autoplayMs": 5200}),
      HomepageSection(homepage=home, section_id="bestsellers", enabled=True, sort_order=1),
      HomepageSection(homepage=home, section_id="promoStrip", enabled=True, sort_order=2),
      HomepageSection(homepage=home, section_id="newArrivals", enabled=True, sort_order=3),
      HomepageSection(homepage=home, section_id="appBanner", enabled=True, sort_order=4),
      HomepageSection(homepage=home, section_id="skinConcerns", enabled=True, sort_order=5),
      HomepageSection(homepage=home, section_id="reels", enabled=True, sort_order=6),
      HomepageSection(homepage=home, section_id="features", enabled=True, sort_order=7),
      HomepageSection(homepage=home, section_id="story", enabled=True, sort_order=8),
      HomepageSection(homepage=home, section_id="logos", enabled=True, sort_order=9),
      HomepageSection(homepage=home, section_id="testimonials", enabled=True, sort_order=10),
    ]
  )
  return home


class HomepageBuilderView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/homepage_builder.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    home = _get_active_homepage()
    ctx["home"] = home
    ctx["sections"] = home.sections.all().order_by("sort_order", "id")
    return ctx


class HomepageSectionOrderView(LoginRequiredMixin, StaffRequiredMixin, View):
  """
  HTMX/AJAX endpoint: updates ordering and enabled toggles.
  """

  def post(self, request: HttpRequest) -> HttpResponse:
    home = _get_active_homepage()
    # expected payload: order[]=section_id...
    order = request.POST.getlist("order[]") or request.POST.getlist("order")
    enabled_map = {k.replace("enabled_", ""): v for k, v in request.POST.items() if k.startswith("enabled_")}
    titles = {k.replace("title_", ""): v for k, v in request.POST.items() if k.startswith("title_")}
    subtitles = {k.replace("subtitle_", ""): v for k, v in request.POST.items() if k.startswith("subtitle_")}
    bgs = {k.replace("bg_", ""): v for k, v in request.POST.items() if k.startswith("bg_")}
    settings_json = {k.replace("settings_", ""): v for k, v in request.POST.items() if k.startswith("settings_")}
    hero_autoplay = request.POST.get("hero_autoplayMs")

    with transaction.atomic():
      if order:
        for idx, sid in enumerate(order):
          HomepageSection.objects.filter(homepage=home, section_id=sid).update(sort_order=idx)
      for sid, v in enabled_map.items():
        HomepageSection.objects.filter(homepage=home, section_id=sid).update(enabled=(v == "1"))
      # update titles/settings
      for sid, t in titles.items():
        HomepageSection.objects.filter(homepage=home, section_id=sid).update(title=(t or "")[:80])
      for sid, sub in subtitles.items():
        hs = HomepageSection.objects.filter(homepage=home, section_id=sid).first()
        if not hs:
          continue
        st = dict(hs.settings or {})
        # merge optional JSON editor
        raw = (settings_json.get(sid) or "").strip()
        if raw:
          try:
            import json

            parsed = json.loads(raw)
            if isinstance(parsed, dict):
              st.update(parsed)
          except Exception:
            pass
        st["subtitle"] = (sub or "")[:160]
        if sid in bgs:
          bg = bgs.get(sid) or ""
          st["bg"] = bg[:220]
        if sid == "hero" and hero_autoplay:
          try:
            st["autoplayMs"] = int(hero_autoplay)
          except Exception:
            pass
        hs.settings = st
        hs.save(update_fields=["settings", "updated_at"])

    return JsonResponse({"ok": True})


class HeroSlidesView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/hero_slides.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    home = _get_active_homepage()
    ctx["home"] = home
    ctx["slides"] = HeroSlide.objects.filter(homepage=home).order_by("sort_order", "id")
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    home = _get_active_homepage()
    # Create slide (minimal; edit page handles the rest)
    slide = HeroSlide.objects.create(homepage=home, sort_order=HeroSlide.objects.filter(homepage=home).count())
    return redirect("dashboard:hero_slide_edit", pk=slide.pk)


class HeroSlideEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/hero_slide_edit.html"

  def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    slide = get_object_or_404(HeroSlide, pk=pk)
    form = HeroSlideForm(instance=slide)
    return render(request, self.template_name, {"slide": slide, "form": form})

  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    slide = get_object_or_404(HeroSlide, pk=pk)
    form = HeroSlideForm(request.POST, request.FILES, instance=slide)
    if form.is_valid():
      slide = form.save(commit=False)

      def create_asset(upload, title):
        if not upload:
          return None
        asset, _, _ = create_media_asset(
          file=upload,
          kind="image",
          title=title[:120],
          alt=title[:180],
          context=MediaAsset.Context.HOMEPAGE,
          cms_section="hero",
        )
        return asset

      bg_up = form.cleaned_data.get("background_upload")
      ca = form.cleaned_data.get("card_a_upload")
      cb = form.cleaned_data.get("card_b_upload")
      cc = form.cleaned_data.get("card_c_upload")
      if bg_up:
        slide.background = create_asset(bg_up, f"Hero background {slide.id}")
      if ca:
        slide.card_a = create_asset(ca, f"Hero card A {slide.id}")
      if cb:
        slide.card_b = create_asset(cb, f"Hero card B {slide.id}")
      if cc:
        slide.card_c = create_asset(cc, f"Hero card C {slide.id}")

      slide.save()
      return redirect("dashboard:hero_slides")
    return render(request, self.template_name, {"slide": slide, "form": form})


class HeroSlideDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    slide = get_object_or_404(HeroSlide, pk=pk)
    slide.delete()
    return redirect("dashboard:hero_slides")


class HeroSlidesOrderView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest) -> HttpResponse:
    home = _get_active_homepage()
    order = request.POST.getlist("order[]") or request.POST.getlist("order")
    enabled_map = {k.replace("enabled_", ""): v for k, v in request.POST.items() if k.startswith("enabled_")}
    with transaction.atomic():
      if order:
        for idx, sid in enumerate(order):
          HeroSlide.objects.filter(homepage=home, pk=int(sid)).update(sort_order=idx)
      for sid, v in enabled_map.items():
        HeroSlide.objects.filter(homepage=home, pk=int(sid)).update(enabled=(v == "1"))
    return JsonResponse({"ok": True})


class PromoStripEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/promo.html"

  def _get_obj(self):
    home = _get_active_homepage()
    obj = PromoStrip.objects.filter(homepage=home).order_by("sort_order", "id").first()
    if obj:
      return obj
    return PromoStrip.objects.create(homepage=home, enabled=True, sort_order=0, title="Get a FREEBIE", subtitle="on orders ₹799+ • auto-added at checkout", pills=["Free gifts"], button_label="Unlock offer", button_href="shop.html")

  def get(self, request: HttpRequest) -> HttpResponse:
    obj = self._get_obj()
    form = PromoStripForm(instance=obj)
    return render(request, self.template_name, {"form": form, "obj": obj})

  def post(self, request: HttpRequest) -> HttpResponse:
    obj = self._get_obj()
    form = PromoStripForm(request.POST, instance=obj)
    if form.is_valid():
      form.save()
      return redirect("dashboard:promo")
    return render(request, self.template_name, {"form": form, "obj": obj})


class AppBannerEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/app_banner.html"

  def _get_obj(self):
    home = _get_active_homepage()
    obj = AppBanner.objects.filter(homepage=home).order_by("sort_order", "id").first()
    if obj:
      return obj
    return AppBanner.objects.create(
      homepage=home,
      enabled=True,
      sort_order=0,
      title="Download app now",
      subtitle="Exclusive drops, early access & rewards — in your pocket.",
      stores=[{"kind": "apple", "title": "App Store", "label": "Download on the", "href": "#"}, {"kind": "google", "title": "Google Play", "label": "Get it on", "href": "#"}],
    )

  def get(self, request: HttpRequest) -> HttpResponse:
    obj = self._get_obj()
    form = AppBannerForm(instance=obj)
    return render(request, self.template_name, {"form": form, "obj": obj})

  def post(self, request: HttpRequest) -> HttpResponse:
    obj = self._get_obj()
    form = AppBannerForm(request.POST, instance=obj)
    if form.is_valid():
      form.save()
      return redirect("dashboard:app_banner")
    return render(request, self.template_name, {"form": form, "obj": obj})


class TestimonialsView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/testimonials.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    home = _get_active_homepage()
    ctx["items"] = Testimonial.objects.filter(homepage=home).order_by("sort_order", "id")
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    home = _get_active_homepage()
    t = Testimonial.objects.create(homepage=home, enabled=True, sort_order=Testimonial.objects.filter(homepage=home).count(), name="New testimonial", text="Write review…", rating=5)
    return redirect("dashboard:testimonial_edit", pk=t.pk)


class TestimonialEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/testimonial_edit.html"

  def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    t = get_object_or_404(Testimonial, pk=pk)
    assets = MediaAsset.objects.order_by("-created_at")[:80]
    return render(request, self.template_name, {"t": t, "assets": assets})

  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    t = get_object_or_404(Testimonial, pk=pk)
    t.enabled = request.POST.get("enabled") == "1"
    t.sort_order = int(request.POST.get("sort_order") or 0)
    t.name = (request.POST.get("name") or "")[:60]
    t.meta = (request.POST.get("meta") or "")[:80]
    try:
      t.rating = float(request.POST.get("rating") or 5)
    except Exception:
      t.rating = 5
    t.text = request.POST.get("text") or ""
    ava_id = request.POST.get("avatar_id") or ""
    if ava_id.isdigit():
      t.avatar_id = int(ava_id)
    t.save()
    return redirect("dashboard:testimonials")


class TestimonialDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    t = get_object_or_404(Testimonial, pk=pk)
    t.delete()
    return redirect("dashboard:testimonials")


class FeaturedLogosView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/logos.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    home = _get_active_homepage()
    ctx["items"] = FeaturedLogo.objects.filter(homepage=home).order_by("sort_order", "id")
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    home = _get_active_homepage()
    l = FeaturedLogo.objects.create(homepage=home, enabled=True, sort_order=FeaturedLogo.objects.filter(homepage=home).count(), name="New logo")
    return redirect("dashboard:logo_edit", pk=l.pk)


class FeaturedLogoEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/logo_edit.html"

  def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    l = get_object_or_404(FeaturedLogo, pk=pk)
    assets = MediaAsset.objects.order_by("-created_at")[:100]
    return render(request, self.template_name, {"l": l, "assets": assets})

  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    l = get_object_or_404(FeaturedLogo, pk=pk)
    l.enabled = request.POST.get("enabled") == "1"
    l.sort_order = int(request.POST.get("sort_order") or 0)
    l.name = (request.POST.get("name") or "")[:40]
    logo_id = request.POST.get("logo_id") or ""
    if logo_id.isdigit():
      l.logo_id = int(logo_id)
    l.save()
    return redirect("dashboard:logos")


class FeaturedLogoDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    l = get_object_or_404(FeaturedLogo, pk=pk)
    l.delete()
    return redirect("dashboard:logos")


class NavigationEditorView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/navigation.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    menu = NavigationMenu.objects.filter(is_active=True).order_by("-updated_at").first()
    if not menu:
      menu = NavigationMenu.objects.create(name="Primary", is_active=True)
    ctx["menu"] = menu
    ctx["links"] = menu.links.all().order_by("sort_order", "id")
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    menu = NavigationMenu.objects.filter(is_active=True).order_by("-updated_at").first()
    if not menu:
      menu = NavigationMenu.objects.create(name="Primary", is_active=True)
    label = (request.POST.get("label") or "").strip()[:40]
    href = (request.POST.get("href") or "").strip()[:240]
    is_pill = request.POST.get("is_pill") == "1"
    if label and href:
      NavigationLink.objects.create(menu=menu, label=label, href=href, is_pill=is_pill, sort_order=menu.links.count())
    return redirect("dashboard:navigation")


class NavigationOrderView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest) -> HttpResponse:
    menu = NavigationMenu.objects.filter(is_active=True).order_by("-updated_at").first()
    if not menu:
      return JsonResponse({"ok": False}, status=400)
    order = request.POST.getlist("order[]") or request.POST.getlist("order")
    enabled_map = {k.replace("enabled_", ""): v for k, v in request.POST.items() if k.startswith("enabled_")}
    delete_map = {k.replace("delete_", ""): v for k, v in request.POST.items() if k.startswith("delete_")}
    with transaction.atomic():
      if order:
        for idx, pk in enumerate(order):
          if pk.isdigit():
            NavigationLink.objects.filter(menu=menu, pk=int(pk)).update(sort_order=idx)
      for pk, v in enabled_map.items():
        if pk.isdigit():
          NavigationLink.objects.filter(menu=menu, pk=int(pk)).update(is_enabled=(v == "1"))
      for pk, v in delete_map.items():
        if v == "1" and pk.isdigit():
          NavigationLink.objects.filter(menu=menu, pk=int(pk)).delete()
    return JsonResponse({"ok": True})


class FooterEditorView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/footer.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    footer = FooterSetting.objects.order_by("-updated_at").first()
    if not footer:
      footer = FooterSetting.objects.create(name="Default", about_text="Premium beauty essentials.", chips=["Dermat-tested"])
    ctx["footer"] = footer
    import json

    payload = {
      "aboutText": footer.about_text,
      "chips": footer.chips or [],
      "bottomLeft": footer.bottom_left,
      "bottomRight": footer.bottom_right,
      "columns": [],
    }
    for col in footer.columns.all().order_by("sort_order", "id"):
      payload["columns"].append(
        {
          "title": col.title,
          "muted": col.muted,
          "links": [{"label": l.label, "href": l.href} for l in col.links.all().order_by("sort_order", "id")],
          "social": [{"label": s.label, "href": s.href, "aria": s.aria_label or s.label} for s in col.social_links.all().order_by("sort_order", "id")],
        }
      )
    ctx["footer_json"] = json.dumps(payload, ensure_ascii=False, indent=2)
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    footer = FooterSetting.objects.order_by("-updated_at").first()
    if not footer:
      footer = FooterSetting.objects.create(name="Default")
    raw = request.POST.get("footer_json") or "{}"
    try:
      import json

      data = json.loads(raw) if raw else {}
      if not isinstance(data, dict):
        data = {}
    except Exception:
      data = {}

    footer.about_text = (data.get("aboutText") or "")[:1000]
    footer.bottom_left = (data.get("bottomLeft") or "")[:140]
    footer.bottom_right = (data.get("bottomRight") or "")[:140]
    chips = data.get("chips") or []
    footer.chips = [str(x)[:60] for x in chips if str(x).strip()][:12]
    footer.save()

    cols = data.get("columns") or []
    if isinstance(cols, list):
      # rebuild columns/links/social as a single atomic edit
      with transaction.atomic():
        footer.columns.all().delete()
        for cidx, col in enumerate(cols[:6]):
          if not isinstance(col, dict):
            continue
          col_obj = FooterColumn.objects.create(
            footer=footer,
            title=str(col.get("title") or "")[:50],
            muted=str(col.get("muted") or "")[:120],
            sort_order=cidx,
          )
          links = col.get("links") or []
          if isinstance(links, list):
            for lidx, l in enumerate(links[:12]):
              if not isinstance(l, dict):
                continue
              FooterLink.objects.create(
                column=col_obj,
                label=str(l.get("label") or "")[:80],
                href=str(l.get("href") or "")[:240],
                sort_order=lidx,
              )
          socials = col.get("social") or []
          if isinstance(socials, list):
            for sidx, s in enumerate(socials[:8]):
              if not isinstance(s, dict):
                continue
              FooterSocialLink.objects.create(
                column=col_obj,
                label=str(s.get("label") or "")[:10],
                href=str(s.get("href") or "")[:240],
                aria_label=str(s.get("aria") or "")[:60],
                sort_order=sidx,
              )
    return redirect("dashboard:footer")


class HomepageVisualEditorView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/homepage_editor.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    home = _get_active_homepage()
    ctx["home"] = home
    import json

    sections = list(home.sections.all().order_by("sort_order", "id"))
    for s in sections:
      try:
        s.settings_json = json.dumps(s.settings or {}, ensure_ascii=False, indent=2)
      except Exception:
        s.settings_json = "{}"
    ctx["sections"] = sections
    ctx["slides"] = home.hero_slides.all().order_by("sort_order", "id")
    return ctx


@method_decorator(xframe_options_sameorigin, name='dispatch')
class PreviewHomeView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  """
  Preview inside the visual editor iframe. Uses the same premium frontend but listens for live patches.
  """

  template_name = "dashboard/preview_home.html"


class ProductSectionsView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/product_sections.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    home = _get_active_homepage()
    ctx["items"] = ProductSection.objects.filter(homepage=home).order_by("sort_order", "id")
    return ctx


class ProductSectionEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/product_section_edit.html"

  def _get_obj(self, kind: str) -> ProductSection:
    home = _get_active_homepage()
    obj = ProductSection.objects.filter(homepage=home, kind=kind).first()
    if obj:
      return obj
    return ProductSection.objects.create(homepage=home, kind=kind, enabled=True, sort_order=0, title=kind, subtitle="", view_all_href="", tabs=[])

  def get(self, request: HttpRequest, kind: str) -> HttpResponse:
    obj = self._get_obj(kind)
    form = ProductSectionForm(instance=obj)
    return render(request, self.template_name, {"obj": obj, "form": form})

  def post(self, request: HttpRequest, kind: str) -> HttpResponse:
    obj = self._get_obj(kind)
    form = ProductSectionForm(request.POST, instance=obj)
    if form.is_valid():
      form.save()
      return redirect("dashboard:product_sections")
    return render(request, self.template_name, {"obj": obj, "form": form})


class ProductListView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/products.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    q = (self.request.GET.get("q") or "").strip()
    qs = Product.objects.select_related("category", "subcategory", "brand_ref").order_by("-updated_at")
    if q:
      qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__icontains=q) | Q(brand_ref__name__icontains=q))
    ctx["q"] = q
    products = list(qs[:200])
    # low stock flag (safe + small N)
    low_ids = set(
      Variant.objects.filter(product_id__in=[p.id for p in products], is_active=True, track_inventory=True)
      .filter(stock__lte=F("low_stock_threshold"))
      .values_list("product_id", flat=True)
      .distinct()
    )
    ctx["low_ids"] = low_ids
    ctx["products"] = products
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    action = (request.POST.get("action") or "").strip()
    ids = [int(x) for x in (request.POST.getlist("ids") or []) if str(x).isdigit()]
    if not ids or action not in ["publish", "unpublish", "activate", "deactivate"]:
      return redirect("dashboard:products")

    qs = Product.objects.filter(pk__in=ids)
    if action == "publish":
      qs.update(is_published=True)
    elif action == "unpublish":
      qs.update(is_published=False)
    elif action == "activate":
      qs.update(is_active=True)
    elif action == "deactivate":
      qs.update(is_active=False)

    return redirect("dashboard:products")


class ProductEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/product_edit.html"

  def get(self, request: HttpRequest, pk: int | None = None) -> HttpResponse:
    product = Product.objects.filter(pk=pk).first() if pk else None
    form = ProductForm(instance=product)
    variants = Variant.objects.filter(product=product).order_by("id") if product else []
    gallery = ProductImage.objects.select_related("media").filter(product=product).order_by("sort_order", "id") if product else []
    return render(request, self.template_name, {"form": form, "product": product, "variants": variants, "gallery": gallery, "vform": VariantForm()})

  def post(self, request: HttpRequest, pk: int | None = None) -> HttpResponse:
    product = Product.objects.filter(pk=pk).first() if pk else None
    form = ProductForm(request.POST, request.FILES, instance=product)
    if form.is_valid():
      obj = form.save()
      return redirect("dashboard:product_edit", pk=obj.pk)
    variants = Variant.objects.filter(product=product).order_by("id") if product else []
    gallery = ProductImage.objects.select_related("media").filter(product=product).order_by("sort_order", "id") if product else []
    return render(request, self.template_name, {"form": form, "product": product, "variants": variants, "gallery": gallery, "vform": VariantForm()})


class ProductGalleryUploadView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    files = request.FILES.getlist("gallery_uploads") or []
    featured = request.FILES.get("featured_upload")

    cat = product.category.slug if product.category_id else ""
    sub = product.subcategory.slug if getattr(product, "subcategory_id", None) else ""

    if featured:
      asset, _, _ = create_media_asset(
        file=featured,
        kind="image",
        title=f"{product.name} featured",
        alt=product.name,
        context=MediaAsset.Context.PRODUCTS,
        product_category=cat,
        product_subcategory=sub,
      )
      product.primary_media = asset
      product.save(update_fields=["primary_media", "updated_at"])

    if files:
      start = ProductImage.objects.filter(product=product).count()
      for idx, f in enumerate(files[:24]):
        asset, _, _ = create_media_asset(
          file=f,
          kind="image",
          title=f"{product.name} gallery",
          alt=product.name,
          context=MediaAsset.Context.PRODUCTS,
          product_category=cat,
          product_subcategory=sub,
        )
        ProductImage.objects.create(product=product, media=asset, sort_order=start + idx)

    return redirect("dashboard:product_edit", pk=product.pk)


class ProductGalleryRemoveView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    ids = [int(x) for x in (request.POST.getlist("remove_ids") or []) if str(x).isdigit()]
    if ids:
      ProductImage.objects.filter(product=product, pk__in=ids).delete()
    return redirect("dashboard:product_edit", pk=product.pk)


class ProductGalleryOrderView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> JsonResponse:
    product = get_object_or_404(Product, pk=pk)
    order = request.POST.getlist("order[]") or request.POST.getlist("order")
    if not order:
      return JsonResponse({"ok": True})
    with transaction.atomic():
      for idx, pid in enumerate(order[:300]):
        if not str(pid).isdigit():
          continue
        ProductImage.objects.filter(product=product, pk=int(pid)).update(sort_order=idx)
    return JsonResponse({"ok": True})


class ProductVariantAddView(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> HttpResponse:
    product = get_object_or_404(Product, pk=pk)
    form = VariantForm(request.POST)
    if form.is_valid():
      v: Variant = form.save(commit=False)
      v.product = product
      v.save()
    return redirect("dashboard:product_edit", pk=product.pk)


class BrandsView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/brands_manage.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["brands"] = Brand.objects.order_by("name")
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    name = (request.POST.get("name") or "").strip()
    if name:
      Brand.objects.get_or_create(name=name[:80])
    return redirect("dashboard:brands_manage")


class SubCategoriesView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/subcategories_manage.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["categories"] = Category.objects.order_by("name")
    ctx["subs"] = SubCategory.objects.select_related("category").order_by("category__name", "name")
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    name = (request.POST.get("name") or "").strip()
    cat_id = request.POST.get("category_id") or ""
    if name and str(cat_id).isdigit():
      cat = Category.objects.filter(pk=int(cat_id)).first()
      if cat:
        slug = slugify(name)[:105] or "other"
        SubCategory.objects.get_or_create(category=cat, slug=slug, defaults={"name": name[:80], "is_active": True})
    return redirect("dashboard:subcategories_manage")

class MediaLibraryView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/media.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["assets"] = MediaAsset.objects.order_by("-created_at")[:120]
    return ctx

  def post(self, request: HttpRequest) -> HttpResponse:
    file = request.FILES.get("file")
    kind = request.POST.get("kind") or "image"
    title = request.POST.get("title") or ""
    alt = request.POST.get("alt") or ""
    if file:
      create_media_asset(file=file, kind=kind, title=title[:120], alt=alt[:180], context=MediaAsset.Context.TEMP)
    return redirect("dashboard:media")


class ManageAssetsView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
  template_name = "dashboard/assets.html"

  def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["categories"] = list(Category.objects.order_by("name").values_list("slug", flat=True))
    ctx["assets"] = MediaAsset.objects.order_by("-created_at")[:60]
    ctx["counts"] = {
      "total": MediaAsset.objects.count(),
      "images": MediaAsset.objects.filter(kind=MediaAsset.Kind.IMAGE).count(),
      "videos": MediaAsset.objects.filter(kind=MediaAsset.Kind.VIDEO).count(),
    }
    return ctx


class AssetsListApi(LoginRequiredMixin, StaffRequiredMixin, View):
  def get(self, request: HttpRequest) -> JsonResponse:
    q = (request.GET.get("q") or "").strip()
    kind = (request.GET.get("kind") or "").strip().lower()
    ctx = (request.GET.get("context") or "").strip()
    pc = (request.GET.get("product_category") or "").strip()
    psc = (request.GET.get("product_subcategory") or "").strip()

    qs = search_assets_queryset(q).order_by("-created_at")
    if kind in ["image", "video"]:
      qs = qs.filter(kind=kind)
    if ctx:
      qs = qs.filter(context=ctx)
    if pc:
      qs = qs.filter(product_category=pc)
    if psc:
      qs = qs.filter(product_subcategory=psc)

    items = []
    for a in qs[:240]:
      items.append(
        {
          "id": a.id,
          "kind": a.kind,
          "title": a.title,
          "alt": a.alt,
          "url": a.file.url,
          "filename": a.original_filename or (a.file.name.split("/")[-1] if a.file.name else ""),
          "context": a.context,
          "cms_section": a.cms_section,
          "product_category": a.product_category,
          "product_subcategory": a.product_subcategory,
          "size_bytes": a.size_bytes,
          "created_at": a.created_at.isoformat() if a.created_at else None,
        }
      )

    return JsonResponse(
      {
        "ok": True,
        "items": items,
        "counts": {
          "total": MediaAsset.objects.count(),
          "images": MediaAsset.objects.filter(kind=MediaAsset.Kind.IMAGE).count(),
          "videos": MediaAsset.objects.filter(kind=MediaAsset.Kind.VIDEO).count(),
        },
      }
    )


class AssetsUploadApi(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest) -> JsonResponse:
    files = request.FILES.getlist("files") or ([] if not request.FILES.get("file") else [request.FILES.get("file")])
    if not files:
      return JsonResponse({"ok": False, "error": "missing_file"}, status=400)

    kind = (request.POST.get("kind") or "image").lower()
    title = (request.POST.get("title") or "")[:120]
    alt = (request.POST.get("alt") or "")[:180]
    context = (request.POST.get("context") or MediaAsset.Context.TEMP).strip() or MediaAsset.Context.TEMP
    cms_section = (request.POST.get("cms_section") or "").strip()
    product_category = (request.POST.get("product_category") or "").strip()
    product_subcategory = (request.POST.get("product_subcategory") or "").strip()

    out = []
    for f in files[:24]:
      asset, created, dup = create_media_asset(
        file=f,
        kind=kind,
        title=title or (asset_title_from_filename(getattr(f, "name", ""))),
        alt=alt,
        context=context,
        cms_section=cms_section,
        product_category=product_category,
        product_subcategory=product_subcategory,
      )
      out.append(
        {
          "id": asset.id,
          "kind": asset.kind,
          "title": asset.title,
          "alt": asset.alt,
          "url": asset.file.url,
          "duplicate": bool(dup),
          "created": bool(created),
        }
      )

    return JsonResponse({"ok": True, "items": out})


def asset_title_from_filename(name: str) -> str:
  base = (name or "").split("/")[-1].split("\\")[-1]
  return base[:120]


class AssetsDeleteApi(LoginRequiredMixin, StaffRequiredMixin, View):
  def post(self, request: HttpRequest, pk: int) -> JsonResponse:
    a = MediaAsset.objects.filter(pk=pk).first()
    if not a:
      return JsonResponse({"ok": False, "error": "not_found"}, status=404)

    usage = media_asset_usage(a)
    if usage.get("total_links", 0) > 0:
      return JsonResponse({"ok": False, "error": "in_use", "usage": usage}, status=409)

    a.delete()
    return JsonResponse({"ok": True})


class ThemeEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/theme.html"

  def _get_theme(self) -> ThemeSetting:
    theme = ThemeSetting.objects.filter(is_active=True).order_by("-updated_at").first()
    if theme:
      return theme
    return ThemeSetting.objects.create(name="Default", is_active=True, tokens={"--gc-accent": "#ff2e7a", "--gc-accent-2": "#8a5bff"})

  def get(self, request: HttpRequest) -> HttpResponse:
    theme = self._get_theme()
    form = ThemeForm(instance=theme)
    return render(request, self.template_name, {"form": form, "theme": theme})

  def post(self, request: HttpRequest) -> HttpResponse:
    theme = self._get_theme()
    form = ThemeForm(request.POST, instance=theme)
    if form.is_valid():
      form.save()
      return redirect("dashboard:theme")
    return render(request, self.template_name, {"form": form, "theme": theme})


class AnnouncementEditView(LoginRequiredMixin, StaffRequiredMixin, View):
  template_name = "dashboard/announcement.html"

  def _get_bar(self) -> AnnouncementBar:
    bar = AnnouncementBar.objects.order_by("-updated_at").first()
    if bar:
      return bar
    return AnnouncementBar.objects.create(
      name="Primary",
      enabled=True,
      badge="UP TO 20% OFF",
      text="on glow bundles + free gifts on ₹799+",
      cta_text="Shop deals",
      cta_href="shop.html",
    )

  def get(self, request: HttpRequest) -> HttpResponse:
    bar = self._get_bar()
    form = AnnouncementForm(instance=bar)
    return render(request, self.template_name, {"form": form, "bar": bar})

  def post(self, request: HttpRequest) -> HttpResponse:
    bar = self._get_bar()
    form = AnnouncementForm(request.POST, instance=bar)
    if form.is_valid():
      form.save()
      return redirect("dashboard:announcement")
    return render(request, self.template_name, {"form": form, "bar": bar})
