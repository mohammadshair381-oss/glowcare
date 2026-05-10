from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


UserModel = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
  def authenticate(self, request, username=None, password=None, **kwargs):
    if username is None:
      username = kwargs.get(UserModel.USERNAME_FIELD)
    if username is None or password is None:
      return None

    user = UserModel.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()
    if not user:
      return None
    if not user.check_password(password):
      return None
    if not self.user_can_authenticate(user):
      return None
    return user

