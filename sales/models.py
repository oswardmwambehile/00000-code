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

class Sales(models.Model):
    company = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales")
    contact_person = models.ForeignKey(CustomerContact, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")

    # ✅ Link to multiple ProductInterests
    product_interests = models.ManyToManyField(ProductInterest, blank=True, related_name="sales")

    contact_number = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Open")
    item_discussed = models.TextField(blank=True)
    is_order_final = models.BooleanField(default=False)
    reason_lost = models.TextField(blank=True, null=True)

    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_added")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale - {self.company.company_name} ({self.status})"





from django.db import models
from sales.models import Sales   # adjust import if Sales is in another app
from products.models import Product  # adjust import if Product is in another app

class SalesItem(models.Model):
    sales = models.ForeignKey(
        Sales,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sales_items"
    )
    price = models.DecimalField(max_digits=19, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales_item"
        verbose_name = "Sales Item"
        verbose_name_plural = "Sales Items"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product} - {self.price} ({self.sales})"

