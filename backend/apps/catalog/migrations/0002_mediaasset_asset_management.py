from django.db import migrations, models

import apps.catalog.media_storage


class Migration(migrations.Migration):
  dependencies = [
    ("catalog", "0001_initial"),
  ]

  operations = [
    migrations.AddField(
      model_name="mediaasset",
      name="context",
      field=models.CharField(choices=[("homepage", "Homepage"), ("banners", "Banners"), ("brands", "Brands"), ("products", "Products"), ("promos", "Promos"), ("cms_sections", "CMS sections"), ("temp", "Temp")], default="temp", max_length=32),
    ),
    migrations.AddField(
      model_name="mediaasset",
      name="cms_section",
      field=models.CharField(blank=True, default="", max_length=80),
    ),
    migrations.AddField(
      model_name="mediaasset",
      name="product_category",
      field=models.CharField(blank=True, default="", max_length=80),
    ),
    migrations.AddField(
      model_name="mediaasset",
      name="product_subcategory",
      field=models.CharField(blank=True, default="", max_length=80),
    ),
    migrations.AddField(
      model_name="mediaasset",
      name="sha256",
      field=models.CharField(blank=True, db_index=True, default="", max_length=64),
    ),
    migrations.AddField(
      model_name="mediaasset",
      name="original_filename",
      field=models.CharField(blank=True, default="", max_length=240),
    ),
    migrations.AddField(
      model_name="mediaasset",
      name="content_type",
      field=models.CharField(blank=True, default="", max_length=120),
    ),
    migrations.AddField(
      model_name="mediaasset",
      name="size_bytes",
      field=models.BigIntegerField(blank=True, null=True),
    ),
    migrations.AlterField(
      model_name="mediaasset",
      name="file",
      field=models.FileField(upload_to=apps.catalog.media_storage.media_asset_upload_to),
    ),
  ]

