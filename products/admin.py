from django.contrib import admin
from .models import Product, ProductInterest


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(ProductInterest)
class ProductInterestAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "created_at", "updated_at")
    list_filter = ("product", "created_at")
    search_fields = ("product__name",)
    readonly_fields = ("created_at", "updated_at")  # prevent manual editing
    ordering = ("-created_at",)
