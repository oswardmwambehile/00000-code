from django.db import models
from customers.models import Customer, CustomerContact
from products.models import ProductInterest
from django.contrib.auth import get_user_model

User = get_user_model()

STATUS_CHOICES = [
    ("Open", "Open"),
    ("Won Paid", "Won Paid"),
    ("Won Pending Payment", "Won Pending Payment"),
    ("Lost", "Lost"),
]

PAYMENT_CHOICES = [
    ("Yes-Full", "Yes-Full"),
    ("Yes-Partial", "Yes-Partial"),
    ("No", "No"),
]

CONTRACT_CHOICES = [
    ("Won", "Won"),
    ("Lost", "Lost"),
]

STAGE_STATUS_MAP = {
    "Prospecting": "Open",
    "Qualifying": "Open",
    "Proposal or Negotiation": "Open",
    "Closing": "Won Pending Payment",
    "Payment Followup": "Won Paid",
}


class Sales(models.Model):
    company = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sales"
    )
    contact_number = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Open", blank=True, null=True)
    product_interests = models.ManyToManyField(ProductInterest, blank=True, related_name="sales")
    is_order_final = models.BooleanField(default=False, blank=True, null=True)
    reason_lost = models.TextField(blank=True, null=True)
    client_budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    contract_outcome = models.CharField(max_length=10, choices=CONTRACT_CHOICES, blank=True, null=True)
    is_payment_collected = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_added")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Sale - {self.company.company_name if self.company else 'Unknown'} ({self.status})"

    def update_status(self):
        """
        Dynamically update sales status based on contract outcome and payment.
        """
        if self.contract_outcome == "Lost":
            self.status = "Lost"
        elif self.contract_outcome == "Won":
            if self.is_payment_collected == "Yes-Full":
                self.status = "Won Paid"
            elif self.is_payment_collected == "Yes-Partial":
                self.status = "Won Pending Payment"
            else:
                self.status = "Won Pending Payment"
        else:
            stage = getattr(self.company, "acquisition_stage", None)
            self.status = STAGE_STATUS_MAP.get(stage, "Open")

        self.save()


class SalesItem(models.Model):
    sales = models.ForeignKey(
        Sales,
        on_delete=models.CASCADE,
        related_name="items",
        blank=True,
        null=True
    )
    product = models.ForeignKey(
        ProductInterest,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sales_items"
    )
    price = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = "sales_item"
        verbose_name = "Sales Item"
        verbose_name_plural = "Sales Items"
        ordering = ["-created_at"]

    def __str__(self):
        # Get company name
        company_name = self.sales.company.company_name if self.sales and self.sales.company else "Unknown Company"
        
        # Get product name via ProductInterest -> Product
        product_name = self.product.product.name if self.product and self.product.product else "Unknown Product"
        
        # Show price
        return f"{company_name} - {product_name} - {self.price if self.price else 0}"
