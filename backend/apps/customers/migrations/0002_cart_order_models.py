from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
  dependencies = [
    ("catalog", "0001_initial"),
    ("customers", "0001_initial"),
    migrations.swappable_dependency(settings.AUTH_USER_MODEL),
  ]

  operations = [
    migrations.CreateModel(
      name="Cart",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("session_key", models.CharField(blank=True, max_length=64, null=True, unique=True)),
        ("coupon_code", models.CharField(blank=True, default="", max_length=20)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="cart", to=settings.AUTH_USER_MODEL)),
      ],
    ),
    migrations.CreateModel(
      name="ShippingAddress",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("full_name", models.CharField(max_length=120)),
        ("phone", models.CharField(max_length=30)),
        ("email", models.EmailField(blank=True, default="", max_length=254)),
        ("pincode", models.CharField(max_length=12)),
        ("address1", models.CharField(max_length=220)),
        ("address2", models.CharField(blank=True, default="", max_length=220)),
        ("city", models.CharField(max_length=80)),
        ("state", models.CharField(max_length=80)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shipping_addresses", to=settings.AUTH_USER_MODEL)),
      ],
    ),
    migrations.CreateModel(
      name="Order",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
        ("payment_method", models.CharField(choices=[("upi", "UPI"), ("card", "Card"), ("cod", "COD")], default="upi", max_length=16)),
        ("payment_status", models.CharField(choices=[("unpaid", "Unpaid"), ("paid", "Paid"), ("refunded", "Refunded")], default="unpaid", max_length=16)),
        ("fulfillment_status", models.CharField(choices=[("placed", "Placed"), ("processing", "Processing"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("canceled", "Canceled")], default="placed", max_length=16)),
        ("coupon_code", models.CharField(blank=True, default="", max_length=20)),
        ("subtotal", models.PositiveIntegerField(default=0)),
        ("discount", models.PositiveIntegerField(default=0)),
        ("shipping_fee", models.PositiveIntegerField(default=0)),
        ("total", models.PositiveIntegerField(default=0)),
        ("currency", models.CharField(default="INR", max_length=8)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("shipping_address", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="customers.shippingaddress")),
        ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to=settings.AUTH_USER_MODEL)),
      ],
    ),
    migrations.CreateModel(
      name="CartItem",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("variant_sku", models.CharField(max_length=50)),
        ("qty", models.PositiveSmallIntegerField(default=1)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("cart", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="customers.cart")),
        ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="catalog.product")),
      ],
      options={"unique_together": {("cart", "product", "variant_sku")}},
    ),
    migrations.CreateModel(
      name="OrderItem",
      fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("variant_sku", models.CharField(max_length=50)),
        ("qty", models.PositiveSmallIntegerField(default=1)),
        ("product_name", models.CharField(blank=True, default="", max_length=180)),
        ("unit_price", models.PositiveIntegerField(default=0)),
        ("line_total", models.PositiveIntegerField(default=0)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="customers.order")),
        ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="+", to="catalog.product")),
      ],
    ),
  ]

