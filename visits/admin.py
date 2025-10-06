from django.contrib import admin
from .models import Visit
from customers.models import Customer, CustomerContact

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company",
        "contact_person",
        "contact_number",
        "designation",
        "meeting_type",
        "status",
        "added_by",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "meeting_type", "created_at")
    search_fields = (
        "company__company_name",
        "contact_person__contact_name",
        "added_by__username",
        "item_discussed",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Visit Info", {
            "fields": (
                "company",
                "contact_person",
                "contact_number",
                "designation",
                "item_discussed",
                "sales",
                "meeting_type",
                "status",
            )
        }),
        ("Location", {
            "fields": ("latitude", "longitude", "visit_image")
        }),
        ("Audit Info", {
            "fields": ("added_by", "created_at", "updated_at")
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("company", "contact_person", "sales", "added_by")

# Optional: inline visits in Customer admin
class VisitInline(admin.TabularInline):
    model = Visit
    fields = ("contact_person", "meeting_type", "status", "created_at")
    readonly_fields = ("created_at",)
    extra = 0
    show_change_link = True

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("company_name", "email", "designation", "acquisition_stage", "created_at")
    search_fields = ("company_name", "email")
    inlines = [VisitInline]
