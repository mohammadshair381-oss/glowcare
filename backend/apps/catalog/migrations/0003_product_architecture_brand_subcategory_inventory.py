import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ("catalog", "0002_mediaasset_asset_management"),
  ]

  operations = [
    migrations.CreateModel(
      name="Brand",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("name", models.CharField(max_length=80, unique=True)),
        ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
        ("is_active", models.BooleanField(default=True)),
      ],
      options={"ordering": ["name"]},
    ),
    migrations.CreateModel(
      name="SubCategory",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("name", models.CharField(max_length=80)),
        ("slug", models.SlugField(blank=True, max_length=110)),
        ("is_active", models.BooleanField(default=True)),
        ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subcategories", to="catalog.category")),
      ],
      options={"ordering": ["category__name", "name"], "unique_together": {("category", "slug")}},
    ),
    migrations.AddField(
      model_name="product",
      name="brand_ref",
      field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="products", to="catalog.brand"),
    ),
    migrations.AddField(
      model_name="product",
      name="subcategory",
      field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="catalog.subcategory"),
    ),
    migrations.AddField(
      model_name="variant",
      name="track_inventory",
      field=models.BooleanField(default=True),
    ),
    migrations.AddField(
      model_name="variant",
      name="low_stock_threshold",
      field=models.PositiveIntegerField(default=5),
    ),
  ]

