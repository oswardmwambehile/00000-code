from django import forms
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from customers.models import Customer, CustomerContact
from products.models import ProductInterest
from .models import Sales, SalesItem

# ------------------- SalesForm -------------------
class SalesForm(forms.ModelForm):
    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "readonly": "readonly",
            "id": "id_contact_number"
        })
    )

    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "readonly": "readonly",
            "id": "id_designation"
        })
    )

    class Meta:
        model = Sales
        fields = [
            "company",
            "contact_person",
            "contact_number",
            "designation",
            "item_discussed",
            "product_interests"
        ]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select", "id": "id_company"}),
            "contact_person": forms.Select(attrs={"class": "form-select", "id": "id_contact_person"}),
            "item_discussed": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "product_interests": forms.SelectMultiple(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = Customer.objects.all().order_by("company_name")
        self.fields["contact_person"].queryset = CustomerContact.objects.none()
        self.fields["contact_person"].empty_label = "Select company first"

        company_id = None
        if self.data.get("company"):
            try:
                company_id = int(self.data.get("company"))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and getattr(self.instance, "company_id", None):
            company_id = self.instance.company_id

        if company_id:
            self.fields["contact_person"].queryset = CustomerContact.objects.filter(
                customer_id=company_id
            ).order_by("contact_name")
            self.fields["contact_person"].empty_label = "Select contact"


class UpdateSalesForm(forms.ModelForm):
    client_budget = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label="Client Budget",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Sales
        fields = ["status", "is_order_final", "reason_lost"]

    def __init__(self, *args, **kwargs):
        stage = kwargs.pop("stage", None)
        super().__init__(*args, **kwargs)

        # Hide only other stage-specific fields
        self.fields["is_order_final"].widget = forms.HiddenInput()
        self.fields["reason_lost"].widget = forms.HiddenInput()

        # Pre-fill client budget from Customer model
        if self.instance.company:
            self.fields["client_budget"].initial = self.instance.company.client_budget

        # Stage-specific logic
        if stage == "Qualifying":
            self.fields["client_budget"].required = True
        elif stage == "Proposal or Negotiation":
            self.fields["is_order_final"].widget = forms.CheckboxInput()
        elif stage == "Closing":
            self.fields["reason_lost"].widget = forms.Textarea()

# ------------------- SalesItemForm -------------------
class SalesItemForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = ["product", "price"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select", "readonly": "readonly", "disabled": True}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None:
            return Decimal(price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return price


SalesItemFormSet = forms.modelformset_factory(
    SalesItem,
    form=SalesItemForm,
    extra=0,
    can_delete=False
)
