from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy


class DashboardLoginView(LoginView):
  template_name = "dashboard/login.html"
  redirect_authenticated_user = True
  next_page = reverse_lazy("dashboard:home")

  def form_valid(self, form):
    resp = super().form_valid(form)
    user = self.request.user
    if not getattr(user, "is_staff", False):
      logout(self.request)
      form.add_error(None, "This account is not allowed to access the dashboard.")
      return self.form_invalid(form)
    return resp


def dashboard_logout(request: HttpRequest) -> HttpResponse:
  logout(request)
  return redirect("dashboard:login")
