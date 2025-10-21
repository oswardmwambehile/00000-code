from django.contrib import admin
from .models import Verification

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "content_object_display",
        "status",
        "sent_to_display",
        "verified_by_display",
        "verified_at",
        "created_at",
    )
    list_filter = ("status", "content_type", "sent_to")
    search_fields = ("message",)
    readonly_fields = ("verified_at", "created_at", "verified_by", "content_object_display")

    fieldsets = (
        (None, {
            "fields": (
                "content_type",
                "object_id",
                "status",
                "message",
            )
        }),
        ("Verification Info", {
            "fields": ("sent_to", "verified_by", "verified_at", "created_at")
        }),
    )

    # Display the actual related object
    def content_object_display(self, obj):
        return str(obj.content_object)
    content_object_display.short_description = "Object"

    # Display first + last name for sent_to
    def sent_to_display(self, obj):
        if obj.sent_to:
            return f"{obj.sent_to.first_name} {obj.sent_to.last_name}"
        return "-"
    sent_to_display.short_description = "Sent To"

    # Display first + last name for verified_by
    def verified_by_display(self, obj):
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}"
        return "-"
    verified_by_display.short_description = "Verified By"
