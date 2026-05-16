from django import forms

from apps.catalog.models import Brand, Category, MediaAsset, Product, SubCategory, Tag, Variant
from apps.cms.models import AnnouncementBar, AppBanner, FooterColumn, FooterLink, FooterSetting, NavigationLink, NavigationMenu, PromoStrip, ThemeSetting, HeroSlide, FeaturedLogo, Testimonial, HomepageSection, ProductSection


class JsonTextarea(forms.Textarea):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.attrs.setdefault("rows", 4)


class MultipleFileInput(forms.ClearableFileInput):
  allow_multiple_selected = True


class ThemeForm(forms.ModelForm):
  class Meta:
    model = ThemeSetting
    fields = ["name", "is_active", "tokens"]
    widgets = {
      "name": forms.TextInput(attrs={"class": "dinput"}),
      "is_active": forms.CheckboxInput(attrs={}),
      "tokens": JsonTextarea(attrs={"class": "dinput"}),
    }


class AnnouncementForm(forms.ModelForm):
  class Meta:
    model = AnnouncementBar
    fields = ["enabled", "badge", "text", "cta_text", "cta_href", "bg", "start_at", "end_at"]
    widgets = {
      "enabled": forms.CheckboxInput(attrs={}),
      "badge": forms.TextInput(attrs={"class": "dinput"}),
      "text": forms.TextInput(attrs={"class": "dinput"}),
      "cta_text": forms.TextInput(attrs={"class": "dinput"}),
      "cta_href": forms.TextInput(attrs={"class": "dinput"}),
      "bg": forms.TextInput(attrs={"class": "dinput"}),
      "start_at": forms.DateTimeInput(attrs={"class": "dinput"}, format="%Y-%m-%d %H:%M"),
      "end_at": forms.DateTimeInput(attrs={"class": "dinput"}, format="%Y-%m-%d %H:%M"),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Accept ISO-like and common formats
    for f in ["start_at", "end_at"]:
      self.fields[f].input_formats = ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M%z", "%Y-%m-%dT%H:%M"]


class ProductForm(forms.ModelForm):
  concern_tags_csv = forms.CharField(required=False, help_text="Comma-separated, e.g. dullness,barrier", widget=forms.TextInput(attrs={"class": "dinput"}))
  skin_type_tags_csv = forms.CharField(required=False, help_text="Comma-separated, e.g. oily,combination", widget=forms.TextInput(attrs={"class": "dinput"}))
  ingredients_csv = forms.CharField(required=False, help_text="Comma-separated", widget=forms.Textarea(attrs={"class": "dinput", "rows": 3}))

  featured_upload = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={"class": "dinput"}), help_text="Optional. Upload a featured image (saved into structured product folders).")
  # Multi-file widget (Django requires allow_multiple_selected=True for multiple uploads).
  gallery_uploads = forms.FileField(required=False, widget=MultipleFileInput(attrs={"class": "dinput", "multiple": True}), help_text="Optional. Upload multiple gallery images at once.")

  class Meta:
    model = Product
    fields = [
      "sku",
      "name",
      "brand",
      "brand_ref",
      "category",
      "subcategory",
      "description",
      "price",
      "compare_at_price",
      "badge",
      "rating",
      "reviews_count",
      "is_active",
      "is_published",
      "tags",
      "primary_media",
    ]
    widgets = {
      "sku": forms.TextInput(attrs={"class": "dinput"}),
      "name": forms.TextInput(attrs={"class": "dinput"}),
      "brand": forms.TextInput(attrs={"class": "dinput"}),
      "brand_ref": forms.Select(attrs={"class": "dinput"}),
      "category": forms.Select(attrs={"class": "dinput"}),
      "subcategory": forms.Select(attrs={"class": "dinput"}),
      "description": forms.Textarea(attrs={"class": "dinput", "rows": 4}),
      "price": forms.NumberInput(attrs={"class": "dinput"}),
      "compare_at_price": forms.NumberInput(attrs={"class": "dinput"}),
      "badge": forms.Select(attrs={"class": "dinput"}),
      "rating": forms.NumberInput(attrs={"class": "dinput", "step": "0.1"}),
      "reviews_count": forms.NumberInput(attrs={"class": "dinput"}),
      "primary_media": forms.Select(attrs={"class": "dinput"}),
      "is_active": forms.CheckboxInput(attrs={}),
      "is_published": forms.CheckboxInput(attrs={}),
      "tags": forms.SelectMultiple(attrs={"class": "dinput"}),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Ensure categories exist
    if not Category.objects.exists():
      for name in ["skincare", "hair", "makeup", "fragrance"]:
        Category.objects.get_or_create(name=name)
    self.fields["primary_media"].queryset = MediaAsset.objects.order_by("-created_at")
    self.fields["brand_ref"].queryset = Brand.objects.filter(is_active=True).order_by("name")
    self.fields["subcategory"].queryset = SubCategory.objects.select_related("category").filter(is_active=True).order_by("category__name", "name")
    self.fields["tags"].queryset = Tag.objects.order_by("name")
    self.fields["brand"].help_text = "Optional. If you select a Brand, this text will be used as fallback for older records."
    if self.instance and self.instance.pk:
      self.fields["concern_tags_csv"].initial = ",".join(self.instance.concern_tags or [])
      self.fields["skin_type_tags_csv"].initial = ",".join(self.instance.skin_type_tags or [])
      self.fields["ingredients_csv"].initial = ", ".join(self.instance.ingredients or [])

  def clean_concern_tags_csv(self):
    raw = self.cleaned_data.get("concern_tags_csv", "")
    return [x.strip() for x in raw.split(",") if x.strip()]

  def clean_skin_type_tags_csv(self):
    raw = self.cleaned_data.get("skin_type_tags_csv", "")
    return [x.strip() for x in raw.split(",") if x.strip()]

  def clean_ingredients_csv(self):
    raw = self.cleaned_data.get("ingredients_csv", "")
    # allow comma or newline separated
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    return [x for x in parts if x]

  def save(self, commit=True):
    obj: Product = super().save(commit=False)
    obj.concern_tags = self.cleaned_data.get("concern_tags_csv", [])
    obj.skin_type_tags = self.cleaned_data.get("skin_type_tags_csv", [])
    obj.ingredients = self.cleaned_data.get("ingredients_csv", [])
    if commit:
      obj.save()
      self.save_m2m()
    return obj


class VariantForm(forms.ModelForm):
  class Meta:
    model = Variant
    fields = ["sku", "shade", "size_ml", "stock", "is_active"]
    widgets = {
      "sku": forms.TextInput(attrs={"class": "dinput"}),
      "shade": forms.TextInput(attrs={"class": "dinput"}),
      "size_ml": forms.NumberInput(attrs={"class": "dinput"}),
      "stock": forms.NumberInput(attrs={"class": "dinput"}),
    }


class PromoStripForm(forms.ModelForm):
  pills_csv = forms.CharField(required=False, help_text="Comma-separated pills", widget=forms.TextInput(attrs={"class": "dinput"}))

  class Meta:
    model = PromoStrip
    fields = ["enabled", "title", "subtitle", "button_label", "button_href", "bg", "start_at", "end_at"]
    widgets = {
      "enabled": forms.CheckboxInput(),
      "title": forms.TextInput(attrs={"class": "dinput"}),
      "subtitle": forms.TextInput(attrs={"class": "dinput"}),
      "button_label": forms.TextInput(attrs={"class": "dinput"}),
      "button_href": forms.TextInput(attrs={"class": "dinput"}),
      "bg": forms.TextInput(attrs={"class": "dinput"}),
      "start_at": forms.DateTimeInput(attrs={"class": "dinput"}, format="%Y-%m-%d %H:%M"),
      "end_at": forms.DateTimeInput(attrs={"class": "dinput"}, format="%Y-%m-%d %H:%M"),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for f in ["start_at", "end_at"]:
      self.fields[f].input_formats = ["%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M%z", "%Y-%m-%dT%H:%M"]
    if self.instance and self.instance.pk:
      self.fields["pills_csv"].initial = ", ".join(self.instance.pills or [])

  def clean_pills_csv(self):
    raw = self.cleaned_data.get("pills_csv", "")
    return [x.strip() for x in raw.split(",") if x.strip()]

  def save(self, commit=True):
    obj: PromoStrip = super().save(commit=False)
    obj.pills = self.cleaned_data.get("pills_csv", [])
    if commit:
      obj.save()
    return obj


class AppBannerForm(forms.ModelForm):
  stores_json = forms.CharField(required=False, help_text='JSON array like [{"kind":"apple","label":"Download on the","title":"App Store","href":"#"}]', widget=JsonTextarea(attrs={"class": "dinput"}))

  class Meta:
    model = AppBanner
    fields = ["enabled", "title", "subtitle", "bg"]
    widgets = {
      "enabled": forms.CheckboxInput(),
      "title": forms.TextInput(attrs={"class": "dinput"}),
      "subtitle": forms.TextInput(attrs={"class": "dinput"}),
      "bg": forms.TextInput(attrs={"class": "dinput"}),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if self.instance and self.instance.pk:
      self.fields["stores_json"].initial = json_dumps(self.instance.stores or [])

  def clean_stores_json(self):
    raw = self.cleaned_data.get("stores_json", "") or "[]"
    try:
      import json

      val = json.loads(raw)
      return val if isinstance(val, list) else []
    except Exception:
      return []

  def save(self, commit=True):
    obj: AppBanner = super().save(commit=False)
    obj.stores = self.cleaned_data.get("stores_json", [])
    if commit:
      obj.save()
    return obj


def json_dumps(obj):
  try:
    import json

    return json.dumps(obj, ensure_ascii=False, indent=2)
  except Exception:
    return "[]"


class HeroSlideForm(forms.ModelForm):
  ribbons_json = forms.CharField(required=False, widget=JsonTextarea(attrs={"class": "dinput"}))
  meta_json = forms.CharField(required=False, widget=JsonTextarea(attrs={"class": "dinput"}))

  # direct upload helpers (create MediaAsset automatically)
  background_upload = forms.FileField(required=False)
  card_a_upload = forms.FileField(required=False)
  card_b_upload = forms.FileField(required=False)
  card_c_upload = forms.FileField(required=False)

  class Meta:
    model = HeroSlide
    fields = [
      "enabled",
      "sort_order",
      "kicker",
      "headline",
      "headline2",
      "sub",
      "primary_label",
      "primary_href",
      "secondary_label",
      "secondary_href",
      "overlay_bg",
      "background",
      "card_a",
      "card_b",
      "card_c",
      "button_styles",
    ]
    widgets = {
      "enabled": forms.CheckboxInput(),
      "sort_order": forms.NumberInput(attrs={"class": "dinput"}),
      "kicker": forms.TextInput(attrs={"class": "dinput"}),
      "headline": forms.TextInput(attrs={"class": "dinput"}),
      "headline2": forms.TextInput(attrs={"class": "dinput"}),
      "sub": forms.Textarea(attrs={"class": "dinput", "rows": 2}),
      "primary_label": forms.TextInput(attrs={"class": "dinput"}),
      "primary_href": forms.TextInput(attrs={"class": "dinput"}),
      "secondary_label": forms.TextInput(attrs={"class": "dinput"}),
      "secondary_href": forms.TextInput(attrs={"class": "dinput"}),
      "overlay_bg": forms.TextInput(attrs={"class": "dinput"}),
      "background": forms.Select(attrs={"class": "dinput"}),
      "card_a": forms.Select(attrs={"class": "dinput"}),
      "card_b": forms.Select(attrs={"class": "dinput"}),
      "card_c": forms.Select(attrs={"class": "dinput"}),
      "button_styles": JsonTextarea(attrs={"class": "dinput", "rows": 4}),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields["background"].queryset = MediaAsset.objects.order_by("-created_at")
    for f in ["card_a", "card_b", "card_c"]:
      self.fields[f].queryset = MediaAsset.objects.order_by("-created_at")
    if self.instance and self.instance.pk:
      self.fields["ribbons_json"].initial = json_dumps(self.instance.ribbons or [])
      self.fields["meta_json"].initial = json_dumps(self.instance.meta or [])

  def clean_ribbons_json(self):
    raw = self.cleaned_data.get("ribbons_json", "") or "[]"
    try:
      import json

      val = json.loads(raw)
      return val if isinstance(val, list) else []
    except Exception:
      return []

  def clean_meta_json(self):
    raw = self.cleaned_data.get("meta_json", "") or "[]"
    try:
      import json

      val = json.loads(raw)
      return val if isinstance(val, list) else []
    except Exception:
      return []

  def save(self, commit=True):
    obj: HeroSlide = super().save(commit=False)
    obj.ribbons = self.cleaned_data.get("ribbons_json", [])
    obj.meta = self.cleaned_data.get("meta_json", [])
    if commit:
      obj.save()
    return obj


class ProductSectionForm(forms.ModelForm):
  tabs_json = forms.CharField(required=False, widget=JsonTextarea(attrs={"class": "dinput", "rows": 8}))

  class Meta:
    model = ProductSection
    fields = ["enabled", "title", "subtitle", "view_all_href"]
    widgets = {
      "enabled": forms.CheckboxInput(),
      "title": forms.TextInput(attrs={"class": "dinput"}),
      "subtitle": forms.TextInput(attrs={"class": "dinput"}),
      "view_all_href": forms.TextInput(attrs={"class": "dinput"}),
    }

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if self.instance and self.instance.pk:
      self.fields["tabs_json"].initial = json_dumps(self.instance.tabs or [])

  def clean_tabs_json(self):
    raw = self.cleaned_data.get("tabs_json", "") or "[]"
    try:
      import json

      val = json.loads(raw)
      return val if isinstance(val, list) else []
    except Exception:
      return []

  def save(self, commit=True):
    obj: ProductSection = super().save(commit=False)
    obj.tabs = self.cleaned_data.get("tabs_json", [])
    if commit:
      obj.save()
    return obj
