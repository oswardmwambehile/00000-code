from django.db import models
from customers.models import Customer

class Product(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProductInterest(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)  # auto set on create
    updated_at = models.DateTimeField(auto_now=True) 
    def __str__(self):
        return f" {self.product}"
