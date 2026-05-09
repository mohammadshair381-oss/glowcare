from django.urls import path

from .views import HomepageView, ProductDetailView, ProductListView


urlpatterns = [
  path("homepage/", HomepageView.as_view(), name="homepage"),
  path("products/", ProductListView.as_view(), name="products_list"),
  path("products/<int:pk>/", ProductDetailView.as_view(), name="products_detail"),
]

