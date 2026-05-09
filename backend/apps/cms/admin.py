from django.contrib import admin

from .models import (
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


class NavigationLinkInline(admin.TabularInline):
  model = NavigationLink
  extra = 0


@admin.register(NavigationMenu)
class NavigationMenuAdmin(admin.ModelAdmin):
  list_display = ["name", "is_active"]
  inlines = [NavigationLinkInline]


class FooterColumnInline(admin.TabularInline):
  model = FooterColumn
  extra = 0


@admin.register(FooterSetting)
class FooterSettingAdmin(admin.ModelAdmin):
  list_display = ["name"]
  inlines = [FooterColumnInline]


class FooterLinkInline(admin.TabularInline):
  model = FooterLink
  extra = 0


class FooterSocialLinkInline(admin.TabularInline):
  model = FooterSocialLink
  extra = 0


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
  list_display = ["footer", "title", "sort_order"]
  inlines = [FooterLinkInline, FooterSocialLinkInline]


@admin.register(ThemeSetting)
class ThemeSettingAdmin(admin.ModelAdmin):
  list_display = ["name", "is_active"]


@admin.register(AnnouncementBar)
class AnnouncementBarAdmin(admin.ModelAdmin):
  list_display = ["name", "enabled", "start_at", "end_at"]


class HomepageSectionInline(admin.TabularInline):
  model = HomepageSection
  extra = 0


@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
  list_display = ["name", "is_active", "theme", "menu", "footer", "announcement"]
  inlines = [HomepageSectionInline]


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
  list_display = ["id", "homepage", "enabled", "sort_order", "headline", "headline2"]
  list_filter = ["homepage", "enabled"]


@admin.register(PromoStrip)
class PromoStripAdmin(admin.ModelAdmin):
  list_display = ["title", "homepage", "enabled", "sort_order", "start_at", "end_at"]


@admin.register(AppBanner)
class AppBannerAdmin(admin.ModelAdmin):
  list_display = ["title", "homepage", "enabled", "sort_order"]


@admin.register(FeaturedLogo)
class FeaturedLogoAdmin(admin.ModelAdmin):
  list_display = ["name", "homepage", "enabled", "sort_order"]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
  list_display = ["name", "homepage", "enabled", "sort_order", "rating"]


@admin.register(ProductSection)
class ProductSectionAdmin(admin.ModelAdmin):
  list_display = ["kind", "homepage", "enabled", "sort_order"]
  filter_horizontal = ["pinned_products"]
