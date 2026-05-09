from django.urls import path

from .views_editor_api import (
  EditorStateView,
  HomepageApplyView,
  MediaListCreateView,
  MediaDeleteView,
  HeroSlideCreateView,
  HeroSlideUpdateView,
  HeroSlideDeleteViewApi,
  TestimonialCreateView,
  TestimonialUpdateView,
  TestimonialDeleteViewApi,
  FeaturedLogoCreateView,
  FeaturedLogoUpdateView,
  FeaturedLogoDeleteViewApi,
  ProductSectionUpdateView,
)


urlpatterns = [
  path("state/", EditorStateView.as_view(), name="editor_state"),
  path("apply/", HomepageApplyView.as_view(), name="homepage_apply"),

  path("media/", MediaListCreateView.as_view(), name="media_list_create"),
  path("media/<int:pk>/delete/", MediaDeleteView.as_view(), name="media_delete"),

  path("hero-slides/", HeroSlideCreateView.as_view(), name="hero_slide_create"),
  path("hero-slides/<int:pk>/", HeroSlideUpdateView.as_view(), name="hero_slide_update"),
  path("hero-slides/<int:pk>/delete/", HeroSlideDeleteViewApi.as_view(), name="hero_slide_delete_api"),

  path("testimonials/", TestimonialCreateView.as_view(), name="testimonial_create"),
  path("testimonials/<int:pk>/", TestimonialUpdateView.as_view(), name="testimonial_update"),
  path("testimonials/<int:pk>/delete/", TestimonialDeleteViewApi.as_view(), name="testimonial_delete_api"),

  path("logos/", FeaturedLogoCreateView.as_view(), name="logo_create"),
  path("logos/<int:pk>/", FeaturedLogoUpdateView.as_view(), name="logo_update"),
  path("logos/<int:pk>/delete/", FeaturedLogoDeleteViewApi.as_view(), name="logo_delete_api"),

  path("product-sections/<int:pk>/", ProductSectionUpdateView.as_view(), name="product_section_update"),
]
