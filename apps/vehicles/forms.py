from datetime import date

from django import forms

from .models import Vehicle


class VehicleForm(forms.ModelForm):
    inspection_date = forms.DateField(
        label="Muayene Tarihi",
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
    )

    field_order = [
        "plate", "brand", "model_name", "year", "chassis_no", "status",
        "inspection_date", "next_maintenance_date", "fleet_contract_end_date", "daily_price",
    ]

    class Meta:
        model = Vehicle
        fields = [
            "plate", "brand", "model_name", "year", "chassis_no", "status",
            "next_maintenance_date", "fleet_contract_end_date", "daily_price",
        ]
        widgets = {
            "plate": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.TextInput(attrs={"class": "form-control"}),
            "model_name": forms.TextInput(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control"}),
            "chassis_no": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "next_maintenance_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "fleet_contract_end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "daily_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            inspection = getattr(self.instance, "inspection", None)
            if inspection:
                self.fields["inspection_date"].initial = inspection.next_inspection_date

    def save(self, commit=True):
        vehicle = super().save(commit=commit)
        inspection_date = self.cleaned_data.get("inspection_date")
        if commit and inspection_date:
            from apps.maintenance.models import Inspection

            existing = getattr(vehicle, "inspection", None)
            Inspection.objects.update_or_create(
                vehicle=vehicle,
                defaults={
                    "next_inspection_date": inspection_date,
                    "last_inspection_date": existing.last_inspection_date if existing else date.today(),
                },
            )
        return vehicle
