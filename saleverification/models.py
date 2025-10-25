from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from sales.models import Sales

User = get_user_model()

VERIFICATION_STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Returned", "Returned"),
]

class SalesVerification(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")  # Points to Sales or other models

    # User who submits the verification request
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_verifications_submitted",
        help_text="User who submitted this record for verification"
    )

    # User who verifies it (usually the supervisor)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_verifications_done",
        help_text="User who performed the verification"
    )

    # Supervisor assigned to verify
    sent_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sales_verifications_assigned",
        help_text="Supervisor assigned to verify this record"
    )

    status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default="Pending"
    )

    # 💬 Separate messages
    user_message = models.TextField(
        blank=True, null=True,
        help_text="Message from the user when submitting verification"
    )
    supervisor_message = models.TextField(
        blank=True, null=True,
        help_text="Supervisor feedback or verification note"
    )

    verified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sales Verification"
        verbose_name_plural = "Sales Verifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.content_type} #{self.object_id} - {self.status}"
    



class SalesVerificationMessage(models.Model):
    verification = models.ForeignKey(
        SalesVerification, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        first = self.sender.first_name or ""
        last = self.sender.last_name or ""
        full_name = f"{first} {last}".strip()
        return f"{full_name}: {self.message[:30]}"

