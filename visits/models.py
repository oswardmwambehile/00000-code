from django.db import models
from customers.models import Customer
from customers.models import Customer, CustomerContact
from products.models import ProductInterest
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from sales.models import Sales  # import your Sales model

User = get_user_model()

MEETING_TYPE_CHOICES = [
    ("In Person", "In Person"),
    ("Phone Call", "Phone Call"),
]

STATUS_CHOICES = [
    ("Open", "Open"),
    ("Approved", "Approved"),
    ("Cancelled", "Cancelled"),
]

class Visit(models.Model):
    company = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        null=True,        # ✅ allow null for migration
        blank=True ,       # ✅ allow blank in forms
        related_name="visits"   # ✅ changed from "sales" to "visits"
    )
    contact_person = models.ForeignKey(
        CustomerContact, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="visit_contacts"   # ✅ changed from "sales" to "visit_contacts"
    )
    contact_number = models.CharField(max_length=255, null=True,  blank=True)
    designation = models.CharField(max_length=255, null=True,  blank=True)

    item_discussed = models.TextField(null=True,  blank=True)

    sales = models.ForeignKey(
        Sales, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="visits",
        help_text="Related sales record (optional)."
    )
    added_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="visits_made",
        help_text="User who made the visit."
    )
    meeting_type = models.CharField(
        max_length=20, 
        choices=MEETING_TYPE_CHOICES,
        help_text="Type of meeting (In Person, Phone Call)."
    )

    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Latitude of visit location."
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Longitude of visit location."
    )

    visit_image = models.ImageField(
        upload_to="visits/", 
        null=True, 
        blank=True,
        help_text="Upload an image related to the visit."
    )

    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default="Open",
        help_text="Status of the visit."
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True,  blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True,  blank=True)

    class Meta:
        verbose_name = "Visit"
        verbose_name_plural = "Visits"
        ordering = ["-created_at"]

    def __str__(self):
        if self.sales and self.sales.company:
            return f"Visit to {self.sales.company.company_name} on {self.created_at.strftime('%Y-%m-%d')}"
        return f"Visit #{self.id} on {self.created_at.strftime('%Y-%m-%d')}"
