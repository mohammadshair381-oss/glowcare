from django.contrib import admin

from .models import Brand, Category, MediaAsset, Product, ProductImage, SubCategory, Tag, Variant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ["name", "slug", "is_active"]
  search_fields = ["name", "slug"]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
  list_display = ["name", "slug", "category", "is_active"]
  list_filter = ["category", "is_active"]
  search_fields = ["name", "slug", "category__name", "category__slug"]


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
  list_display = ["name", "slug", "is_active"]
  list_filter = ["is_active"]
  search_fields = ["name", "slug"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
  list_display = ["name", "slug"]
  search_fields = ["name", "slug"]


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
  list_display = ["id", "kind", "title", "file", "created_at"]
  search_fields = ["title", "file"]
  list_filter = ["kind"]


class VariantInline(admin.TabularInline):
  model = Variant
  extra = 1


class ProductImageInline(admin.TabularInline):
  model = ProductImage
  extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ["sku", "name", "brand", "brand_ref", "category", "subcategory", "price", "badge", "is_published", "is_active"]
  list_filter = ["badge", "is_active", "is_published", "category", "subcategory", "brand_ref"]
  search_fields = ["sku", "name", "brand", "brand_ref__name"]
  inlines = [VariantInline, ProductImageInline]


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
  list_display = ["sku", "product", "size_ml", "shade", "stock", "track_inventory", "low_stock_threshold", "is_active"]
  list_filter = ["is_active"]
  search_fields = ["sku", "product__name"]
