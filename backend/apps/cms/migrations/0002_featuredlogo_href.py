from django.db import migrations, models


class Migration(migrations.Migration):
  dependencies = [
    ("cms", "0001_initial"),
  ]

  operations = [
    migrations.AddField(
      model_name="featuredlogo",
      name="href",
      field=models.CharField(blank=True, default="", max_length=240),
    ),
  ]

