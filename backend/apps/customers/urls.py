from django.urls import path

from .views import (
  CustomerAccountView,
  CustomerCheckoutView,
  CustomerLoginView,
  CustomerPasswordResetCompleteView,
  CustomerPasswordResetConfirmView,
  CustomerPasswordResetDoneView,
  CustomerPasswordResetView,
  CustomerPaymentView,
  CustomerSignupView,
  CustomerSuccessView,
  customer_logout,
)


app_name = "customers"


urlpatterns = [
  path("login.html", CustomerLoginView.as_view(), name="login"),
  path("signup.html", CustomerSignupView.as_view(), name="signup"),
  path("logout/", customer_logout, name="logout"),

  path("forgot.html", CustomerPasswordResetView.as_view(), name="password_reset"),
  path("forgot/sent/", CustomerPasswordResetDoneView.as_view(), name="password_reset_done"),
  path("reset/<uidb64>/<token>/", CustomerPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
  path("reset/complete/", CustomerPasswordResetCompleteView.as_view(), name="password_reset_complete"),

  path("account.html", CustomerAccountView.as_view(), name="account"),
  path("checkout.html", CustomerCheckoutView.as_view(), name="checkout"),
  path("payment.html", CustomerPaymentView.as_view(), name="payment"),
  path("success.html", CustomerSuccessView.as_view(), name="success"),
]

