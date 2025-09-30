from decimal import Decimal, ROUND_HALF_UP
from django import forms
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


from django import forms
from django.db.models import Sum
from .models import Sales, SalesItem
from django import forms
from django.db.models import Sum
from .models import Sales, PAYMENT_CHOICES, CONTRACT_CHOICES

class UpdateSalesForm(forms.ModelForm):
    # ----------------- General fields -----------------
    client_budget = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label="Client Budget",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    # ----------------- Closing stage fields -----------------
    contract_outcome = forms.ChoiceField(
    choices=[('', '--- Select ---')] + list(CONTRACT_CHOICES),
    required=False,
    label="Contract Outcome",
    widget=forms.Select(attrs={"class": "form-control"})
)

    is_payment_collected = forms.ChoiceField(
    choices=[('', '--- Select ---')] + list(PAYMENT_CHOICES),  # blank first option
    required=False,
    label="Payment Collected",
    widget=forms.Select(attrs={"class": "form-control"})
)

    closing_amount = forms.DecimalField(
        max_digits=19,
        decimal_places=2,
        required=False,
        label="Contract Amount",
        widget=forms.NumberInput(attrs={"class": "form-control", "disabled": "disabled"})
    )

    reason_lost = forms.CharField(
        required=False,
        label="Reason for Lost",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2})
    )

    class Meta:
        model = Sales
        fields = [
            "is_order_final",
            "reason_lost",
            "contract_outcome",
            "is_payment_collected",
        ]

    def __init__(self, *args, **kwargs):
        stage = kwargs.pop("stage", None)
        super().__init__(*args, **kwargs)

        # Pre-fill client budget from company
        if self.instance.company:
            self.fields["client_budget"].initial = self.instance.company.client_budget

        # Qualifying stage: client_budget is required
        if stage == "Qualifying":
            self.fields["client_budget"].required = True

        # Closing stage: calculate total and show fields
        if stage == "Closing":
            total = self.instance.items.aggregate(total=Sum('price'))['total'] or 0
            self.fields["closing_amount"].initial = total

        # Ensure fields are always rendered; JS will handle visibility
        for field_name in ["contract_outcome", "is_payment_collected", "closing_amount", "reason_lost"]:
            self.fields[field_name].widget.attrs.update({
                "class": self.fields[field_name].widget.attrs.get("class", "") + " form-control"
            })

    def clean(self):
        cleaned_data = super().clean()
        contract_outcome = cleaned_data.get("contract_outcome")
        is_payment_collected = cleaned_data.get("is_payment_collected")
        reason_lost = cleaned_data.get("reason_lost")

        # Closing stage validation
        if contract_outcome == "Lost" and not reason_lost:
            self.add_error("reason_lost", "Reason for lost is required if contract is lost.")

        if contract_outcome == "Won" and not is_payment_collected:
            self.add_error("is_payment_collected", "Please select payment status if contract is won.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Update status automatically based on contract outcome + payment
        instance.update_status()
        if commit:
            instance.save()
        return instance


# ------------------- SalesItemForm -------------------

# ------------------- SalesItemForm -------------------
class SalesItemForm(forms.ModelForm):
    class Meta:
        model = SalesItem
        fields = ["price"]  # Only price, product is linked via product_interests
        widgets = {
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter price"
            }),
        }

    def __init__(self, *args, **kwargs):
        stage = kwargs.pop("stage", None)
        super().__init__(*args, **kwargs)
        # Price is required in Proposal stage
        if stage == "Proposal or Negotiation":
            self.fields["price"].required = True

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None:
            return Decimal(price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return price


# ------------------- SalesItemFormSet -------------------
from django.forms import modelformset_factory

SalesItemFormSet = modelformset_factory(
    SalesItem,
    form=SalesItemForm,
    extra=0,
    can_delete=False
)
