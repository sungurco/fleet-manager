from django import forms

from .models import SystemSettings


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ["economy_provision_amount", "luxury_provision_amount"]
        widgets = {
            "economy_provision_amount": forms.TextInput(
                attrs={"class": "form-control money-input", "inputmode": "decimal", "autocomplete": "off"}
            ),
            "luxury_provision_amount": forms.TextInput(
                attrs={"class": "form-control money-input", "inputmode": "decimal", "autocomplete": "off"}
            ),
        }
