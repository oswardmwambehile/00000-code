# visits/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Visit
from sales.models import Sales

# Ensure Sales is registered
@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    search_fields = ("company__company_name", "contact_person__contact_name")

# Visit Admin
@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sales_link",
        "customer_name",
        "added_by_name",
        "send_to_name",
        "meeting_type",
        "status",
        "created_at",
        "visit_image_preview"
    )
    list_filter = ("status", "meeting_type", "created_at")
    search_fields = (
        "sales__company__company_name",
        "sales__contact_person__contact_name",
        "added_by__first_name",
        "added_by__last_name",
        "send_to__first_name",
        "send_to__last_name",
    )
    autocomplete_fields = ("sales", "added_by", "send_to")
    readonly_fields = ("visit_image_preview",)

    def customer_name(self, obj):
        if obj.sales and obj.sales.company:
            return obj.sales.company.company_name
        return "-"
    customer_name.short_description = "Customer"

    def sales_link(self, obj):
        if obj.sales:
            url = f"/admin/sales/sales/{obj.sales.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.sales)
        return "-"
    sales_link.short_description = "Sales"

    def added_by_name(self, obj):
        if obj.added_by:
            return f"{obj.added_by.first_name} {obj.added_by.last_name}"
        return "-"
    added_by_name.short_description = "Added By"

    def send_to_name(self, obj):
        if obj.send_to:
            return f"{obj.send_to.first_name} {obj.send_to.last_name}"
        return "-"
    send_to_name.short_description = "Send To"

    def visit_image_preview(self, obj):
        if obj.visit_image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.visit_image.url)
        return "-"
    visit_image_preview.short_description = "Visit Image"
