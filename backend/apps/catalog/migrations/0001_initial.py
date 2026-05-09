from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
  initial = True

  dependencies = []

  operations = [
    migrations.CreateModel(
      name="Category",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("name", models.CharField(max_length=80, unique=True)),
        ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
        ("description", models.TextField(blank=True)),
        ("is_active", models.BooleanField(default=True)),
      ],
      options={"ordering": ["name"]},
    ),
    migrations.CreateModel(
      name="MediaAsset",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("kind", models.CharField(choices=[("image", "Image"), ("video", "Video")], default="image", max_length=16)),
        ("file", models.FileField(upload_to="uploads/%Y/%m/")),
        ("alt", models.CharField(blank=True, max_length=180)),
        ("title", models.CharField(blank=True, max_length=120)),
        ("width", models.PositiveIntegerField(blank=True, null=True)),
        ("height", models.PositiveIntegerField(blank=True, null=True)),
      ],
    ),
    migrations.CreateModel(
      name="Tag",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("name", models.CharField(max_length=50, unique=True)),
        ("slug", models.SlugField(blank=True, max_length=60, unique=True)),
      ],
      options={"ordering": ["name"]},
    ),
    migrations.CreateModel(
      name="Product",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("sku", models.CharField(max_length=40, unique=True)),
        ("name", models.CharField(max_length=140)),
        ("slug", models.SlugField(blank=True, max_length=180, unique=True)),
        ("brand", models.CharField(default="GlowCare", max_length=80)),
        ("description", models.TextField(blank=True)),
        ("price", models.PositiveIntegerField(help_text="Price in INR (integer)")),
        ("compare_at_price", models.PositiveIntegerField(blank=True, help_text="Original MRP (optional)", null=True)),
        ("badge", models.CharField(blank=True, choices=[("New", "New"), ("Bestseller", "Bestseller"), ("Trending", "Trending"), ("Hot", "Hot"), ("Featured", "Featured")], max_length=24)),
        ("rating", models.DecimalField(decimal_places=2, default=0, max_digits=3)),
        ("reviews_count", models.PositiveIntegerField(default=0)),
        ("is_active", models.BooleanField(default=True)),
        ("is_published", models.BooleanField(default=True)),
        ("concern_tags", models.JSONField(blank=True, default=list)),
        ("skin_type_tags", models.JSONField(blank=True, default=list)),
        ("ingredients", models.JSONField(blank=True, default=list)),
        ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="catalog.category")),
        ("primary_media", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="primary_for_products", to="catalog.mediaasset")),
      ],
      options={"ordering": ["-updated_at"]},
    ),
    migrations.CreateModel(
      name="ProductImage",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("sort_order", models.PositiveIntegerField(default=0)),
        ("media", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="product_images", to="catalog.mediaasset")),
        ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="catalog.product")),
      ],
      options={"ordering": ["sort_order", "id"]},
    ),
    migrations.CreateModel(
      name="Variant",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("sku", models.CharField(max_length=50)),
        ("shade", models.CharField(blank=True, default="Original", max_length=80)),
        ("size_ml", models.PositiveIntegerField(blank=True, null=True)),
        ("stock", models.PositiveIntegerField(default=0)),
        ("is_active", models.BooleanField(default=True)),
        ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="catalog.product")),
      ],
      options={"ordering": ["id"], "unique_together": {("product", "sku")}},
    ),
    migrations.AddField(
      model_name="product",
      name="tags",
      field=models.ManyToManyField(blank=True, related_name="products", to="catalog.tag"),
    ),
  ]

