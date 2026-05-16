from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class StaffRequiredMixin(UserPassesTestMixin):
  def test_func(self):
    u = self.request.user
    return bool(u and u.is_authenticated and u.is_staff)

  def handle_no_permission(self):
    if not self.request.user.is_authenticated:
      return super().handle_no_permission()
    from django.contrib.auth import logout

    logout(self.request)
    return redirect("dashboard:login")

