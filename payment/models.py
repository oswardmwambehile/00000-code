from django.db import models
from sales.models import Sales, SalesItem # adjust if your Sales model is in a different app

class Payment(models.Model):
    sales = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  # auto set when created
    updated_at = models.DateTimeField(auto_now=True)      # auto update on save
  

    class Meta:
        db_table = "payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} - {self.sales} - {self.amount}"
