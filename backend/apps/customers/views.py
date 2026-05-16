from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View

from .forms import CustomerSignupForm
from .cart_service import merge_session_cart_to_user


class CustomerLoginView(LoginView):
  template_name = "public/login.html"
  redirect_authenticated_user = True

  def form_valid(self, form):
    resp = super().form_valid(form)
    merge_session_cart_to_user(self.request)
    return resp

  def get_success_url(self):
    return self.get_redirect_url() or reverse_lazy("customers:account")


class CustomerSignupView(View):
  template_name = "public/signup.html"

  def get(self, request: HttpRequest) -> HttpResponse:
    form = CustomerSignupForm()
    return render(request, self.template_name, {"form": form, "next": request.GET.get("next", "")})

  def post(self, request: HttpRequest) -> HttpResponse:
    form = CustomerSignupForm(request.POST)
    next_url = request.POST.get("next") or ""
    if not form.is_valid():
      return render(request, self.template_name, {"form": form, "next": next_url})

    user = form.save()
    authed = authenticate(request, username=user.username, password=request.POST.get("password"))
    if authed:
      login(request, authed)
    messages.success(request, "Account created.")

    redirect_to = reverse_lazy("customers:account")
    if next_url and url_has_allowed_host_and_scheme(
      url=next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
      redirect_to = next_url
    return redirect(redirect_to)


@require_POST
def customer_logout(request: HttpRequest) -> HttpResponse:
  logout(request)
  return redirect("public_home")


class CustomerAccountView(LoginRequiredMixin, TemplateView):
  template_name = "public/account.html"
  login_url = reverse_lazy("customers:login")


class CustomerCheckoutView(LoginRequiredMixin, TemplateView):
  template_name = "public/checkout.html"
  login_url = reverse_lazy("customers:login")


class CustomerPaymentView(LoginRequiredMixin, TemplateView):
  template_name = "public/payment.html"
  login_url = reverse_lazy("customers:login")


class CustomerSuccessView(LoginRequiredMixin, TemplateView):
  template_name = "public/success.html"
  login_url = reverse_lazy("customers:login")


class CustomerPasswordResetView(PasswordResetView):
  template_name = "public/forgot.html"
  email_template_name = "registration/password_reset_email.txt"
  subject_template_name = "registration/password_reset_subject.txt"
  success_url = reverse_lazy("customers:password_reset_done")


class CustomerPasswordResetDoneView(PasswordResetDoneView):
  template_name = "public/password_reset_sent.html"


class CustomerPasswordResetConfirmView(PasswordResetConfirmView):
  template_name = "public/password_reset_confirm.html"
  success_url = reverse_lazy("customers:password_reset_complete")


class CustomerPasswordResetCompleteView(PasswordResetCompleteView):
  template_name = "public/password_reset_complete.html"
