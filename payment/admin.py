# payments/admin.py
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "sales", "amount", "created_at", "updated_at")  # columns in admin list
    list_filter = ("created_at", "updated_at", "sales")  # filter sidebar
    search_fields = ("sales__id", "sales__customer__company_name")  # adjust to your Sales model fields
    ordering = ("-created_at",)  # latest first
    readonly_fields = ("created_at", "updated_at")  # not editable in admin
