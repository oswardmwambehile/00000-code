from django.db import models
from customers.models import Customer, CustomerContact
from products.models import ProductInterest
from django.contrib.auth import get_user_model

User = get_user_model()

STATUS_CHOICES = [
    ("Open", "Open"),
    ("Paid", "Paid"),
    ("Won", "Won"),
    ("Lost", "Lost"),
]

class Sales(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sales"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Open",
        blank=True,
        null=True
    )
    product_interests = models.ManyToManyField(
        ProductInterest,
        blank=True,
        null=True,
        related_name="sales",
    )
    is_order_final = models.BooleanField(default=False, blank=True, null=True)
    reason_lost = models.TextField(blank=True, null=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_added"
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Sale for {self.customer.company_name if self.customer else 'Unknown Customer'}"


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
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = "sales_item"
        verbose_name = "Sales Item"
        verbose_name_plural = "Sales Items"
        ordering = ["-created_at"]

    def __str__(self):
        customer_name = self.sales.customer.company_name if self.sales and self.sales.customer else "Unknown Customer"
        product_name = self.product.product.name if self.product and self.product.product else "Unknown Product"
        return f"{customer_name} - {product_name} - {self.price if self.price else 0}"