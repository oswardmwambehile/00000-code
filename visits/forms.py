from django import forms
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from .models import Visit

class NewVisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        # Exclude sales, added_by, and status
        exclude = ["sales", "added_by", "status"]
        widgets = {
            "latitude": forms.HiddenInput(attrs={"id": "id_latitude"}),
            "longitude": forms.HiddenInput(attrs={"id": "id_longitude"}),
            "meeting_type": forms.Select(attrs={"class": "form-select"}),
            "visit_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "send_to": forms.Select(attrs={"class": "form-select"}),  # optional recipient
           
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: customize querysets or initial values if needed

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lon = cleaned.get("longitude")

        if not lat or not lon:
            raise ValidationError("Location not detected. Please allow location access and refresh the page.")

        # Format latitude and longitude to 6 decimals
        try:
            cleaned["latitude"] = Decimal(str(lat)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            cleaned["longitude"] = Decimal(str(lon)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        except Exception:
            raise ValidationError("Invalid coordinates received. Please refresh and try again.")

        return cleaned
