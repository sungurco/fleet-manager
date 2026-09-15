from django import forms

from apps.vehicles.models import Vehicle

from .models import Customer, Driver, Rental


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = [
            "vehicle", "customer", "driver", "start_date", "end_date",
            "pricing_type", "daily_price_snapshot", "total_price",
            "status", "payment_status", "paid_amount",
            "delivery_km", "return_km",
        ]
        widgets = {
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "customer": forms.Select(attrs={"class": "form-select"}),
            "driver": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "pricing_type": forms.Select(attrs={"class": "form-select"}),
            "daily_price_snapshot": forms.TextInput(attrs={"class": "form-control money-input", "inputmode": "decimal", "autocomplete": "off"}),
            "total_price": forms.TextInput(attrs={"class": "form-control money-input", "inputmode": "decimal", "autocomplete": "off", "id": "id_total_price"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "payment_status": forms.Select(attrs={"class": "form-select"}),
            "paid_amount": forms.TextInput(attrs={"class": "form-control money-input", "inputmode": "decimal", "autocomplete": "off"}),
            "delivery_km": forms.NumberInput(attrs={"class": "form-control"}),
            "return_km": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.exclude(status=Vehicle.Status.PASIF).order_by("plate")
        self.fields["customer"].queryset = Customer.objects.order_by("full_name")
        self.fields["driver"].queryset = Driver.objects.select_related("customer").order_by("full_name")
        self.fields["driver"].required = False
        self.fields["driver"].label_from_instance = lambda d: f"{d.full_name} ({d.customer.full_name})"
        self.fields["total_price"].required = False


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_type", "full_name", "tc_no", "phone", "email", "address", "notes",
            "company_title", "tax_office", "tax_no", "billing_address",
            "contact_person_name", "contact_person_phone", "contact_person_email",
        ]
        widgets = {
            "customer_type": forms.Select(attrs={"class": "form-select", "id": "id_customer_type"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "tc_no": forms.TextInput(attrs={"class": "form-control", "maxlength": "11"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "company_title": forms.TextInput(attrs={"class": "form-control"}),
            "tax_office": forms.TextInput(attrs={"class": "form-control"}),
            "tax_no": forms.TextInput(attrs={"class": "form-control", "maxlength": "10"}),
            "billing_address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "contact_person_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person_phone": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person_email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "full_name", "birth_date", "tc_no", "passport_no", "address", "phone",
            "license_no", "license_class", "license_issue_place", "license_issue_date",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "tc_no": forms.TextInput(attrs={"class": "form-control", "maxlength": "11"}),
            "passport_no": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "license_no": forms.TextInput(attrs={"class": "form-control"}),
            "license_class": forms.TextInput(attrs={"class": "form-control"}),
            "license_issue_place": forms.TextInput(attrs={"class": "form-control"}),
            "license_issue_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
        }
