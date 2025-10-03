from django.db import models
from customers.models import Customer

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Product"


class ProductInterest(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)  # auto set on create
    updated_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return f" {self.product}"
