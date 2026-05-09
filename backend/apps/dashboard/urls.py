from django.urls import include, path

from .views_auth import DashboardLoginView, dashboard_logout
from .views_dashboard import (
  AnnouncementEditView,
  DashboardHomeView,
  FooterEditorView,
  HeroSlideEditView,
  HeroSlideDeleteView,
  HeroSlidesView,
  HeroSlidesOrderView,
  HomepageBuilderView,
  HomepageSectionOrderView,
  HomepageVisualEditorView,
  MediaLibraryView,
  NavigationEditorView,
  NavigationOrderView,
  PromoStripEditView,
  AppBannerEditView,
  ProductEditView,
  ProductListView,
  ProductSectionsView,
  ProductSectionEditView,
  ProductVariantAddView,
  FeaturedLogosView,
  FeaturedLogoEditView,
  FeaturedLogoDeleteView,
  TestimonialsView,
  TestimonialEditView,
  TestimonialDeleteView,
  ThemeEditView,
  PreviewHomeView,
)


urlpatterns = [
  path("api/", include(("apps.dashboard.api_urls", "dashboard_api"), namespace="dashboard_api")),
  path("login/", DashboardLoginView.as_view(), name="login"),
  path("logout/", dashboard_logout, name="logout"),

  path("", DashboardHomeView.as_view(), name="home"),
  path("preview/", PreviewHomeView.as_view(), name="preview_home"),
  path("homepage/", HomepageBuilderView.as_view(), name="homepage_builder"),
  path("homepage/editor/", HomepageVisualEditorView.as_view(), name="homepage_editor"),
  path("homepage/sections/order/", HomepageSectionOrderView.as_view(), name="homepage_sections_order"),

  path("hero/", HeroSlidesView.as_view(), name="hero_slides"),
  path("hero/<int:pk>/", HeroSlideEditView.as_view(), name="hero_slide_edit"),
  path("hero/<int:pk>/delete/", HeroSlideDeleteView.as_view(), name="hero_slide_delete"),
  path("hero/order/", HeroSlidesOrderView.as_view(), name="hero_slides_order"),

  path("promo/", PromoStripEditView.as_view(), name="promo"),
  path("app-banner/", AppBannerEditView.as_view(), name="app_banner"),

  path("navigation/", NavigationEditorView.as_view(), name="navigation"),
  path("navigation/order/", NavigationOrderView.as_view(), name="navigation_order"),
  path("footer/", FooterEditorView.as_view(), name="footer"),

  path("logos/", FeaturedLogosView.as_view(), name="logos"),
  path("logos/<int:pk>/", FeaturedLogoEditView.as_view(), name="logo_edit"),
  path("logos/<int:pk>/delete/", FeaturedLogoDeleteView.as_view(), name="logo_delete"),

  path("testimonials/", TestimonialsView.as_view(), name="testimonials"),
  path("testimonials/<int:pk>/", TestimonialEditView.as_view(), name="testimonial_edit"),
  path("testimonials/<int:pk>/delete/", TestimonialDeleteView.as_view(), name="testimonial_delete"),

  path("products/", ProductListView.as_view(), name="products"),
  path("products/new/", ProductEditView.as_view(), name="product_new"),
  path("products/<int:pk>/", ProductEditView.as_view(), name="product_edit"),
  path("products/<int:pk>/variants/add/", ProductVariantAddView.as_view(), name="product_variant_add"),
  path("product-sections/", ProductSectionsView.as_view(), name="product_sections"),
  path("product-sections/<str:kind>/", ProductSectionEditView.as_view(), name="product_section_edit"),

  path("media/", MediaLibraryView.as_view(), name="media"),

  path("theme/", ThemeEditView.as_view(), name="theme"),
  path("announcement/", AnnouncementEditView.as_view(), name="announcement"),
]
