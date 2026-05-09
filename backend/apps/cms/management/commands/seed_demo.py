from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from pathlib import Path

from apps.catalog.models import Category, MediaAsset, Product, Variant
from apps.cms.models import (
  AnnouncementBar,
  AppBanner,
  FooterColumn,
  FooterLink,
  FooterSetting,
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


class Command(BaseCommand):
  help = "Seed demo content for GlowCare CMS (products + homepage)."

  def handle(self, *args, **options):
    repo_root = Path(settings.BASE_DIR).parent

    def ensure_media(rel_path: str, title: str):
      existing = MediaAsset.objects.filter(title=title).first()
      if existing:
        return existing
      src = repo_root / rel_path
      if not src.exists():
        return None
      with src.open("rb") as f:
        asset = MediaAsset.objects.create(kind="image", title=title, alt=title, file=File(f, name=src.name))
      return asset

    p1 = ensure_media("assets/images/products/p1.svg", "Product 1")
    p2 = ensure_media("assets/images/products/p2.svg", "Product 2")
    p3 = ensure_media("assets/images/products/p3.svg", "Product 3")
    p4 = ensure_media("assets/images/products/p4.svg", "Product 4")

    # Categories
    cats = {}
    for slug in ["skincare", "hair", "makeup", "fragrance"]:
      c, _ = Category.objects.get_or_create(name=slug, defaults={"slug": slug})
      cats[slug] = c

    # Theme
    theme, _ = ThemeSetting.objects.get_or_create(
      name="Default",
      defaults={"is_active": True, "tokens": {"--gc-accent": "#ff2e7a", "--gc-accent-2": "#8a5bff", "--brand": "#ff2e7a"}},
    )
    theme.is_active = True
    theme.save()

    # Menu
    menu, _ = NavigationMenu.objects.get_or_create(name="Primary", defaults={"is_active": True})
    if menu.links.count() == 0:
      links = [
        ("Shop All", "shop.html", False),
        ("Skin Concerns", "shop.html?category=skincare", False),
        ("Ingredients", "shop.html?category=skincare", False),
        ("Skin Type", "shop.html?category=skincare", False),
        ("Best Sellers", "shop.html?badge=Bestseller", True),
        ("New Arrivals", "shop.html?badge=New", False),
        ("Blogs", "info.html", False),
      ]
      for i, (label, href, pill) in enumerate(links):
        NavigationLink.objects.create(menu=menu, label=label, href=href, is_pill=pill, sort_order=i)

    # Footer
    footer, _ = FooterSetting.objects.get_or_create(
      name="Default",
      defaults={
        "about_text": "Premium beauty essentials for everyday glow. CMS-driven demo storefront.",
        "chips": ["Dermat-tested", "Cruelty-free", "Made for India"],
        "bottom_left": "© 2026 GlowCare",
        "bottom_right": "Ctrl+Shift+A: admin mode (keyboard-only)",
      },
    )
    if footer.columns.count() == 0:
      shop_col = FooterColumn.objects.create(footer=footer, title="Shop", sort_order=0)
      for i, (label, href) in enumerate(
        [("Skincare", "shop.html?category=skincare"), ("Hair", "shop.html?category=hair"), ("Makeup", "shop.html?category=makeup"), ("Fragrance", "shop.html?category=fragrance")]
      ):
        FooterLink.objects.create(column=shop_col, label=label, href=href, sort_order=i)
      help_col = FooterColumn.objects.create(footer=footer, title="Help", sort_order=1)
      for i, (label, href) in enumerate([("Shipping", "info.html#shipping"), ("Returns", "info.html#returns"), ("Privacy", "info.html#privacy"), ("Terms", "info.html#terms")]):
        FooterLink.objects.create(column=help_col, label=label, href=href, sort_order=i)
      contact_col = FooterColumn.objects.create(footer=footer, title="Contact", muted="Mon–Sat, 10am–6pm IST", sort_order=2)
      FooterLink.objects.create(column=contact_col, label="support@glowcare.example", href="mailto:support@glowcare.example", sort_order=0)
      FooterLink.objects.create(column=contact_col, label="Contact page", href="contact.html", sort_order=1)

    # Announcement
    bar, _ = AnnouncementBar.objects.get_or_create(
      name="Primary",
      defaults={
        "enabled": True,
        "badge": "UP TO 20% OFF",
        "text": "on glow bundles + free gifts on ₹799+",
        "cta_text": "Shop deals",
        "cta_href": "shop.html?badge=Bestseller",
      },
    )

    # Homepage
    home, _ = Homepage.objects.get_or_create(name="Homepage", defaults={"is_active": True})
    home.is_active = True
    home.theme = theme
    home.menu = menu
    home.footer = footer
    home.announcement = bar
    home.save()

    if home.sections.count() == 0:
      default_order = [
        "hero",
        "bestsellers",
        "promoStrip",
        "newArrivals",
        "appBanner",
        "skinConcerns",
        "reels",
        "features",
        "story",
        "logos",
        "testimonials",
      ]
      for idx, sid in enumerate(default_order):
        title_map = {
          "bestsellers": "Bestsellers",
          "newArrivals": "New Arrivals",
          "skinConcerns": "Skin Concerns",
          "reels": "Watch It. Love It",
          "features": "Clean Beauty",
          "story": "Our Story",
          "logos": "Featured In",
          "testimonials": "Feels Good Stories",
        }
        subtitle_map = {
          "bestsellers": "Loved by customers — made for daily use",
          "newArrivals": "Fresh launches to upgrade your routine",
          "skinConcerns": "Tap a concern to shop curated picks",
          "reels": "Reel-style quick looks at your next glow routine",
          "features": "With uncompromised efficacy",
          "story": "Behind the glow — premium care designed for real weather, real skin, real days.",
          "logos": "Spotted where beauty gets serious",
          "testimonials": "Real routines, real results",
        }
        settings = {"autoplayMs": 5200} if sid == "hero" else {}
        if sid in subtitle_map:
          settings["subtitle"] = subtitle_map[sid]
        if sid == "features":
          settings["cards"] = [
            {"title": "Clinically-inspired actives", "desc": "Formulated for visible results without the drama."},
            {"title": "Cruelty-free always", "desc": "Thoughtful choices, kinder routines."},
            {"title": "Plant + lab synergy", "desc": "Modern skincare built on proven science."},
            {"title": "Sensitive-first", "desc": "Comfortable textures, barrier-friendly."},
          ]
        if sid == "story":
          settings["buttonLabel"] = "Read more"
          settings["buttonHref"] = "about.html"
          if p3:
            settings["imageUrl"] = p3.file.url
        HomepageSection.objects.create(homepage=home, section_id=sid, enabled=True, sort_order=idx, title=title_map.get(sid, ""), settings=settings)

    # Products (minimal demo if empty)
    if Product.objects.count() == 0:
      demo = [
        ("GC-101", "10% Vitamin C Glow Serum", "skincare", 499, "Bestseller", ["dullness", "pigmentation"], ["all", "oily", "combination"], ["Vitamin C", "Ferulic Acid", "Hyaluronic Acid"]),
        ("GC-102", "SPF 50 PA++++ Gel Sunscreen", "skincare", 449, "Bestseller", ["tan", "pigmentation", "dullness"], ["all", "oily", "combination"], ["UVA/UVB Filters", "Vitamin E", "Aloe"]),
        ("GC-103", "Barrier Repair Moisturizer (Ceramides)", "skincare", 549, "Trending", ["dryness", "barrier"], ["dry", "normal", "all"], ["Ceramides", "Panthenol", "Niacinamide"]),
        ("GC-104", "Niacinamide + Zinc Pore Serum", "skincare", 399, "Hot", ["pores", "oiliness"], ["oily", "combination"], ["Niacinamide", "Zinc PCA", "Allantoin"]),
      ]
      for sku, name, cat, price, badge, concern, skin, ing in demo:
        p = Product.objects.create(
          sku=sku,
          name=name,
          brand="GlowCare",
          category=cats[cat],
          price=price,
          badge=badge,
          description="Premium, daily-use formula designed for smooth layering.",
          rating=4.6,
          reviews_count=1200,
          concern_tags=concern,
          skin_type_tags=skin,
          ingredients=ing,
          primary_media=p1 if sku.endswith("101") else p2 if sku.endswith("102") else p3 if sku.endswith("103") else p4,
        )
        Variant.objects.create(product=p, sku=f"{sku}-15", size_ml=15, stock=20, shade="Original")
        Variant.objects.create(product=p, sku=f"{sku}-30", size_ml=30, stock=12, shade="Original")

    # Product sections
    ps_best, _ = ProductSection.objects.get_or_create(
      homepage=home,
      kind=ProductSection.Kind.BESTSELLERS,
      defaults={
        "enabled": True,
        "sort_order": 1,
        "title": "Bestsellers",
        "subtitle": "Loved by customers — made for daily use",
        "view_all_href": "shop.html?badge=Bestseller",
        "tabs": [
          {"id": "sunscreen", "label": "Sunscreen", "filter": {"search": "sunscreen"}},
          {"id": "moisturizer", "label": "Moisturiser", "filter": {"search": "moisturizer"}},
          {"id": "serum", "label": "Serum", "filter": {"category": "skincare"}},
        ],
      },
    )
    ps_new, _ = ProductSection.objects.get_or_create(
      homepage=home,
      kind=ProductSection.Kind.NEW_ARRIVALS,
      defaults={
        "enabled": True,
        "sort_order": 3,
        "title": "New Arrivals",
        "subtitle": "Fresh launches to upgrade your routine",
        "view_all_href": "shop.html?badge=New",
        "tabs": [
          {"id": "justin", "label": "Just in", "filter": {"badge": "New"}},
          {"id": "trending", "label": "Trending", "filter": {"badge": "Trending"}},
        ],
      },
    )
    ProductSection.objects.get_or_create(
      homepage=home,
      kind=ProductSection.Kind.SKIN_CONCERNS,
      defaults={
        "enabled": True,
        "sort_order": 5,
        "title": "Skin Concerns",
        "subtitle": "Tap a concern to shop curated picks",
        "view_all_href": "shop.html?category=skincare",
        "tabs": [
          {"id": "dullness", "label": "Dullness", "filter": {"concern": "dullness"}},
          {"id": "barrier", "label": "Barrier", "filter": {"concern": "barrier"}},
          {"id": "pigmentation", "label": "Dark Spots", "filter": {"concern": "pigmentation"}},
        ],
      },
    )

    PromoStrip.objects.get_or_create(
      homepage=home,
      defaults={
        "enabled": True,
        "sort_order": 2,
        "title": "Get a FREEBIE",
        "subtitle": "on orders ₹799+ • auto-added at checkout",
        "pills": ["Free gifts", "Limited-time", "No minimum code"],
        "button_label": "Unlock offer",
        "button_href": "shop.html",
        "bg": "",
      },
    )

    AppBanner.objects.get_or_create(
      homepage=home,
      defaults={
        "enabled": True,
        "sort_order": 4,
        "title": "Download app now",
        "subtitle": "Exclusive drops, early access & rewards — in your pocket.",
        "stores": [
          {"kind": "apple", "title": "App Store", "label": "Download on the", "href": "#"},
          {"kind": "google", "title": "Google Play", "label": "Get it on", "href": "#"},
        ],
        "bg": "",
      },
    )

    if HeroSlide.objects.filter(homepage=home).count() == 0:
      HeroSlide.objects.create(
        homepage=home,
        enabled=True,
        sort_order=0,
        kicker="Meltie craving continues…",
        headline="Berry",
        headline2="Crush",
        sub="Brighten + hydrate with a plush, glassy finish — made for humid days.",
        primary_label="Shop now",
        primary_href="shop.html?badge=Bestseller",
        secondary_label="Explore new",
        secondary_href="shop.html?badge=New",
        card_a=p1,
        card_b=p2,
        card_c=p3,
        ribbons=[{"label": "Free gifts on", "value": "₹799+"}, {"label": "UP TO", "value": "20% OFF"}, {"label": "Derm-tested", "value": "everyday safe"}],
        meta=[{"title": "Free shipping", "desc": "Above ₹499"}, {"title": "Fast delivery", "desc": "2–5 business days"}, {"title": "Easy returns", "desc": "7 days"}],
      )

    if Testimonial.objects.filter(homepage=home).count() == 0:
      Testimonial.objects.create(homepage=home, enabled=True, sort_order=0, name="Megha P.", meta="Combination skin • 2 months", rating=5, text="The sunscreen is genuinely weightless. No cast, no pilling — and it sits beautifully under makeup.")
      Testimonial.objects.create(homepage=home, enabled=True, sort_order=1, name="Reshma S.", meta="Dry skin • 3 weeks", rating=5, text="Barrier moisturizer feels plush but not heavy. My skin looks calmer by day three.")

    self.stdout.write(self.style.SUCCESS("Seeded GlowCare CMS demo content."))
