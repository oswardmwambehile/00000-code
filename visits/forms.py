from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from .models import Visit
from customers.models import CustomerContact, Customer
from sales.models import Sales
from products.models import ProductInterest

class VisitForm(forms.ModelForm):
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

    # Always include sales fields in the form
    client_budget = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        label="Client Budget"
    )
    product_interests = forms.ModelMultipleChoiceField(
        queryset=ProductInterest.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        label="Product Interests"
    )

    class Meta:
        model = Visit
        fields = [
            "company",
            "contact_person",
            "contact_number",
            "designation",
            "item_discussed",
            "meeting_type",
            "latitude",
            "longitude",
            "visit_image",
            "client_budget",
            "product_interests",
        ]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select", "id": "id_company_name"}),
            "contact_person": forms.Select(attrs={"class": "form-select", "id": "id_contact_person"}),
            "item_discussed": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "meeting_type": forms.Select(attrs={"class": "form-select"}),
            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate companies
        self.fields["company"].queryset = Customer.objects.all().order_by("company_name")

        # Default contact_person queryset
        self.fields["contact_person"].queryset = CustomerContact.objects.none()
        self.fields["contact_person"].empty_label = "Select company first"

        # Determine selected company
        company_id = None
        if self.data.get("company"):
            try:
                company_id = int(self.data.get("company"))
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and getattr(self.instance, "company_id", None):
            company_id = self.instance.company_id

        # Populate contact_person based on company
        if company_id:
            self.fields["contact_person"].queryset = CustomerContact.objects.filter(
                customer_id=company_id
            ).order_by("contact_name")
            self.fields["contact_person"].empty_label = "Select contact"

            # Prefill sales fields if sales instance exists
            if self.instance.pk and getattr(self.instance, "sales", None):
                sales_instance = self.instance.sales
                self.fields["client_budget"].initial = sales_instance.client_budget
                self.fields["product_interests"].initial = sales_instance.product_interests.all()

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lon = cleaned.get("longitude")

        if not lat or not lon:
            raise ValidationError("Location not detected. Allow location access and wait for the map.")

        try:
            cleaned["latitude"] = str(
                Decimal(str(lat)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            )
            cleaned["longitude"] = str(
                Decimal(str(lon)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            )
        except Exception:
            raise ValidationError("Invalid coordinates received. Please refresh and try again.")

        return cleaned
