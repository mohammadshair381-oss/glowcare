from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView

from apps.dashboard.views_public import HomePageView


urlpatterns = [
  # Unify admin: legacy Django admin + static admin.html redirect to the dashboard.
  re_path(r"^admin(?:/.*)?$", RedirectView.as_view(url="/dashboard/", permanent=False)),
  path("admin.html", RedirectView.as_view(url="/dashboard/", permanent=False)),

  path("dashboard/", include(("apps.dashboard.urls", "dashboard"), namespace="dashboard")),
  path("api/v1/", include(("apps.api.urls", "api"), namespace="api")),
  path("", include(("apps.customers.urls", "customers"), namespace="customers")),

  # Public frontend entry (renders existing premium UI, content hydrated via API)
  path("", HomePageView.as_view(), name="public_home"),
  path("index.html", RedirectView.as_view(url="/", permanent=False)),
  path("shop.html", TemplateView.as_view(template_name="public/shop.html"), name="public_shop"),
  path("product.html", TemplateView.as_view(template_name="public/product.html"), name="public_product"),

  # Remaining static frontend pages (served as Django templates for correct `{% static %}` paths).
  path("about.html", TemplateView.as_view(template_name="public/about.html"), name="public_about"),
  path("contact.html", TemplateView.as_view(template_name="public/contact.html"), name="public_contact"),
  path("info.html", TemplateView.as_view(template_name="public/info.html"), name="public_info"),

  path("cart.html", TemplateView.as_view(template_name="public/cart.html"), name="public_cart"),
  path("wishlist.html", TemplateView.as_view(template_name="public/wishlist.html"), name="public_wishlist"),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
