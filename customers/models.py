from django.db import models
from django.utils import timezone

DESIGNATION_CHOICES = [
    ('Owner', 'Owner'),
    ('Engineer', 'Engineer'),
    ('Contractor', 'Contractor'),
]

CUSTOMER_TYPES = [
        ('Individual', 'Individual'),
        ('Company', 'Company'),
    ]

ACQUISITION_STAGE_CHOICES = [
    ("Prospecting", "Prospecting"),
    ("Qualifying", "Qualifying"),
    ("Proposal or Negotiation", "Proposal or Negotiation"),
    ("Closing", "Closing"),
    ("Payment Followup", "Payment Followup"),
]


class Customer(models.Model):
    designation = models.CharField(
        max_length=100,
        choices=DESIGNATION_CHOICES
    )
    company_name = models.CharField(
        max_length=200,
        unique=True
    )
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='Individual'
    )
    location = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    acquisition_stage = models.CharField(
        max_length=50,
        choices=ACQUISITION_STAGE_CHOICES,
        default='Prospecting'
    )

   
    client_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated client budget in TZS"
    )

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.company_name


class CustomerContact(models.Model):
    customer = models.ForeignKey(
        Customer,
        related_name="contacts",
        on_delete=models.CASCADE
    )
    contact_name = models.CharField(max_length=150)
    contact_detail = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.contact_name} ({self.customer.company_name})"
