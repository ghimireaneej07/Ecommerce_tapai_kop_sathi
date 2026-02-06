from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ["is_active"]
    search_fields = ["name"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "is_active", "created_at"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "short_description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    
    fieldsets = (
        (None, {
            "fields": ("category", "name", "slug", "is_active")
        }),
        ("Details", {
            "fields": ("short_description", "description", "price", "stock")
        }),
        ("Media", {
            "fields": ("main_image", "image_url"),
            "description": "Upload an image OR provide a URL to download automatically."
        }),
    )
