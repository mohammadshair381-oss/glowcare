from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError

from .models import CustomerProfile


User = get_user_model()

class CustomerSignupForm(forms.Form):
  name = forms.CharField(max_length=150)
  email = forms.EmailField(max_length=254)
  password = forms.CharField(widget=forms.PasswordInput, strip=False)

  def clean_email(self):
    email = str(self.cleaned_data.get("email") or "").strip().lower()
    if not email:
      return email
    if User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
      raise ValidationError("An account with this email already exists.")
    return email

  def clean_password(self):
    password = str(self.cleaned_data.get("password") or "")
    password_validation.validate_password(password)
    return password

  def save(self):
    name = str(self.cleaned_data["name"]).strip()
    email = str(self.cleaned_data["email"]).strip().lower()
    password = str(self.cleaned_data["password"])

    user = User(username=email, email=email, first_name=name, is_staff=False, is_superuser=False)
    user.set_password(password)
    user.full_clean()
    user.save()
    CustomerProfile.objects.create(user=user)
    return user
