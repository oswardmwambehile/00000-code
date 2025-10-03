from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",   # Bootstrap class
                    "placeholder": "Enter product name"
                }
            ),
        }
        labels = {
            "name": "Product Name"  # Custom label (Bootstrap-friendly)
        }
