from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()

VERIFICATION_STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Returned", "Returned"),
]


class Verification(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # User who submits the verification request
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verifications_submitted",
        help_text="User who submitted this record for verification"
    )

    # User who is assigned to verify it
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verifications_done",
        help_text="User who performed the verification"
    )

    # Supervisor assigned to verify this record (same as verified_by in your case)
    sent_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verifications_assigned",
        help_text="Supervisor assigned to verify this record"
    )

    status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default="Pending"
    )

    message = models.TextField(blank=True, null=True)

    verified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Verification"
        verbose_name_plural = "Verifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.content_type} #{self.object_id} - {self.status}"
