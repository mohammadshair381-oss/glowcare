from django.db import models
from django.utils.text import slugify

from apps.catalog.models import MediaAsset, Product


class TimeStampedModel(models.Model):
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    abstract = True


class ThemeSetting(TimeStampedModel):
  """
  Theme tokens editable from dashboard.
  Stored as CSS var dict (e.g. {"--gc-accent":"#ff2e7a"}).
  """

  name = models.CharField(max_length=80, unique=True, default="Default")
  tokens = models.JSONField(default=dict, blank=True)
  is_active = models.BooleanField(default=True)

  def __str__(self):
    return self.name


class NavigationMenu(TimeStampedModel):
  name = models.CharField(max_length=80, unique=True, default="Primary")
  is_active = models.BooleanField(default=True)

  def __str__(self):
    return self.name


class NavigationLink(TimeStampedModel):
  menu = models.ForeignKey(NavigationMenu, on_delete=models.CASCADE, related_name="links")
  label = models.CharField(max_length=40)
  href = models.CharField(max_length=240)
  is_pill = models.BooleanField(default=False)
  sort_order = models.PositiveIntegerField(default=0)
  is_enabled = models.BooleanField(default=True)

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.label


class FooterSetting(TimeStampedModel):
  name = models.CharField(max_length=80, unique=True, default="Default")
  about_text = models.TextField(blank=True)
  chips = models.JSONField(default=list, blank=True)
  bottom_left = models.CharField(max_length=140, blank=True, default="© 2026 GlowCare")
  bottom_right = models.CharField(max_length=140, blank=True, default="Ctrl+Shift+A: admin mode (keyboard-only)")

  def __str__(self):
    return self.name


class FooterColumn(TimeStampedModel):
  footer = models.ForeignKey(FooterSetting, on_delete=models.CASCADE, related_name="columns")
  title = models.CharField(max_length=50)
  muted = models.CharField(max_length=120, blank=True)
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.title


class FooterLink(TimeStampedModel):
  column = models.ForeignKey(FooterColumn, on_delete=models.CASCADE, related_name="links")
  label = models.CharField(max_length=80)
  href = models.CharField(max_length=240)
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.label


class FooterSocialLink(TimeStampedModel):
  column = models.ForeignKey(FooterColumn, on_delete=models.CASCADE, related_name="social_links")
  label = models.CharField(max_length=10)
  href = models.CharField(max_length=240)
  aria_label = models.CharField(max_length=60, blank=True)
  sort_order = models.PositiveIntegerField(default=0)

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.label


class AnnouncementBar(TimeStampedModel):
  """
  Top announcement bar with scheduling.
  """

  name = models.CharField(max_length=80, default="Primary", unique=True)
  enabled = models.BooleanField(default=True)

  badge = models.CharField(max_length=40, blank=True)
  text = models.CharField(max_length=160, blank=True)
  cta_text = models.CharField(max_length=40, blank=True)
  cta_href = models.CharField(max_length=240, blank=True)

  bg = models.CharField(max_length=160, blank=True, help_text="CSS background (optional)")
  start_at = models.DateTimeField(null=True, blank=True)
  end_at = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return self.name

  def is_visible_now(self, now):
    if not self.enabled:
      return False
    if self.start_at and now < self.start_at:
      return False
    if self.end_at and now > self.end_at:
      return False
    return True


class Homepage(TimeStampedModel):
  """
  Singleton-ish homepage config. Keep 1 row active.
  """

  name = models.CharField(max_length=80, unique=True, default="Homepage")
  is_active = models.BooleanField(default=True)

  theme = models.ForeignKey(ThemeSetting, null=True, blank=True, on_delete=models.SET_NULL, related_name="homepages")
  menu = models.ForeignKey(NavigationMenu, null=True, blank=True, on_delete=models.SET_NULL, related_name="homepages")
  footer = models.ForeignKey(FooterSetting, null=True, blank=True, on_delete=models.SET_NULL, related_name="homepages")
  announcement = models.ForeignKey(AnnouncementBar, null=True, blank=True, on_delete=models.SET_NULL, related_name="homepages")

  def __str__(self):
    return self.name


class HomepageSection(TimeStampedModel):
  """
  Controls ordering and toggles for major sections (hero, bestsellers, etc.)
  """

  homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="sections")
  section_id = models.SlugField(max_length=40)
  title = models.CharField(max_length=80, blank=True)
  enabled = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)
  settings = models.JSONField(default=dict, blank=True)

  class Meta:
    unique_together = [("homepage", "section_id")]
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.section_id


class HeroSlide(TimeStampedModel):
  homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="hero_slides")
  enabled = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)

  kicker = models.CharField(max_length=90, blank=True)
  headline = models.CharField(max_length=40, blank=True)
  headline2 = models.CharField(max_length=40, blank=True)
  sub = models.CharField(max_length=220, blank=True)

  primary_label = models.CharField(max_length=30, blank=True)
  primary_href = models.CharField(max_length=240, blank=True)
  secondary_label = models.CharField(max_length=30, blank=True)
  secondary_href = models.CharField(max_length=240, blank=True)

  # Background (image/video)
  background = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="hero_backgrounds")
  overlay_bg = models.CharField(max_length=220, blank=True, help_text="CSS overlay gradient/background for the slide")
  button_styles = models.JSONField(default=dict, blank=True, help_text="Optional button style config")

  # 3 product cards shown at right
  card_a = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="hero_card_a")
  card_b = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="hero_card_b")
  card_c = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="hero_card_c")

  ribbons = models.JSONField(default=list, blank=True)  # list of {label,value}
  meta = models.JSONField(default=list, blank=True)  # list of {title,desc}

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return f"Hero slide {self.id}"


class PromoStrip(TimeStampedModel):
  homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="promo_strips")
  enabled = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)
  title = models.CharField(max_length=70)
  subtitle = models.CharField(max_length=160, blank=True)
  pills = models.JSONField(default=list, blank=True)
  button_label = models.CharField(max_length=30, blank=True)
  button_href = models.CharField(max_length=240, blank=True)
  bg = models.CharField(max_length=220, blank=True, help_text="CSS background override")
  start_at = models.DateTimeField(null=True, blank=True)
  end_at = models.DateTimeField(null=True, blank=True)

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.title


class AppBanner(TimeStampedModel):
  homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="app_banners")
  enabled = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)
  title = models.CharField(max_length=70)
  subtitle = models.CharField(max_length=180, blank=True)
  stores = models.JSONField(default=list, blank=True)  # list of {kind,label,title,href}
  bg = models.CharField(max_length=220, blank=True, help_text="CSS background override")

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.title


class FeaturedLogo(TimeStampedModel):
  homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="featured_logos")
  enabled = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)
  name = models.CharField(max_length=40)
  logo = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="featured_logos")

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.name


class Testimonial(TimeStampedModel):
  homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="testimonials")
  enabled = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)
  name = models.CharField(max_length=60)
  meta = models.CharField(max_length=80, blank=True)
  rating = models.DecimalField(max_digits=3, decimal_places=2, default=5)
  text = models.TextField()
  avatar = models.ForeignKey(MediaAsset, null=True, blank=True, on_delete=models.SET_NULL, related_name="testimonial_avatars")

  class Meta:
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.name


class ProductSection(TimeStampedModel):
  """
  Product rail sections (bestsellers/new arrivals/skin concerns).
  Uses queryset rules + manual pinning.
  """

  class Kind(models.TextChoices):
    BESTSELLERS = "bestsellers", "Bestsellers"
    NEW_ARRIVALS = "newArrivals", "New arrivals"
    SKIN_CONCERNS = "skinConcerns", "Skin concerns"

  homepage = models.ForeignKey(Homepage, on_delete=models.CASCADE, related_name="product_sections")
  kind = models.CharField(max_length=30, choices=Kind.choices)
  enabled = models.BooleanField(default=True)
  sort_order = models.PositiveIntegerField(default=0)

  title = models.CharField(max_length=60)
  subtitle = models.CharField(max_length=160, blank=True)
  view_all_href = models.CharField(max_length=240, blank=True)

  tabs = models.JSONField(default=list, blank=True)  # list of {id,label,filter:{...}}
  pinned_products = models.ManyToManyField(Product, blank=True, related_name="pinned_in_sections")

  class Meta:
    unique_together = [("homepage", "kind")]
    ordering = ["sort_order", "id"]

  def __str__(self):
    return self.kind
