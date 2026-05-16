from django.urls import path

from .views import (
  CartClearView,
  CartCouponView,
  CartItemAddView,
  CartItemDeleteView,
  CartItemQtyView,
  CartView,
  CheckoutPlaceView,
  CheckoutShippingView,
  CsrfCookieView,
  HomepageView,
  OrderDetailView,
  OrderListView,
  ProductDetailView,
  ProductListView,
)


urlpatterns = [
  path("csrf/", CsrfCookieView.as_view(), name="csrf"),
  path("homepage/", HomepageView.as_view(), name="homepage"),
  path("products/", ProductListView.as_view(), name="products_list"),
  path("products/<int:pk>/", ProductDetailView.as_view(), name="products_detail"),

  path("cart/", CartView.as_view(), name="cart"),
  path("cart/items/", CartItemAddView.as_view(), name="cart_item_add"),
  path("cart/items/<int:item_id>/", CartItemQtyView.as_view(), name="cart_item_qty"),
  path("cart/items/<int:item_id>/remove/", CartItemDeleteView.as_view(), name="cart_item_remove"),
  path("cart/clear/", CartClearView.as_view(), name="cart_clear"),
  path("cart/coupon/", CartCouponView.as_view(), name="cart_coupon"),

  path("checkout/shipping/", CheckoutShippingView.as_view(), name="checkout_shipping"),
  path("checkout/place/", CheckoutPlaceView.as_view(), name="checkout_place"),

  path("orders/", OrderListView.as_view(), name="orders_list"),
  path("orders/<uuid:order_id>/", OrderDetailView.as_view(), name="orders_detail"),
]
