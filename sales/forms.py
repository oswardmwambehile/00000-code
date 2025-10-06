


from django import forms
from sales.models import SalesItem

class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = ["price"]
        widgets = {
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter price",
                    "step": "0.01",  # Allows decimals
                }
            ),
        }



