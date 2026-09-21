from django import forms

from apps.vehicles.models import Vehicle

from .models import Address, Customer, Driver, Rental


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = [
            "vehicle", "customer", "driver", "start_date", "end_date",
            "pricing_type", "daily_price_snapshot", "total_price",
            "status", "payment_status", "paid_amount",
            "delivery_km", "return_km", "provision_type",
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
            "provision_type": forms.Select(attrs={"class": "form-select", "id": "id_provision_type"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehicle"].queryset = Vehicle.objects.exclude(status=Vehicle.Status.PASIF).order_by("plate")
        self.fields["customer"].queryset = Customer.objects.order_by("full_name")
        self.fields["driver"].queryset = Driver.objects.select_related("customer").order_by("full_name")
        self.fields["driver"].required = False
        self.fields["driver"].label_from_instance = lambda d: f"{d.full_name} ({d.customer.full_name})"
        self.fields["total_price"].required = False


class RentalCloseForm(forms.Form):
    """Erken iade / kiralama kapatma formu - 'Aracı Teslim Al / Kiralamayı Kapat' aksiyonu için."""

    actual_end_date = forms.DateField(
        label="Fiili Bitiş Tarihi",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
    )
    return_km = forms.IntegerField(
        label="İade Km", required=False, min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    new_total_price = forms.DecimalField(
        label="Yeni (Gerçek) Kiralama Tutarı", max_digits=10, decimal_places=2,
        widget=forms.TextInput(attrs={
            "class": "form-control money-input", "inputmode": "decimal", "autocomplete": "off", "id": "id_new_total_price",
        }),
    )
    deduction_amount = forms.DecimalField(
        label="Ek Ücret / Kesinti", required=False, max_digits=10, decimal_places=2, min_value=0,
        widget=forms.TextInput(attrs={"class": "form-control money-input", "inputmode": "decimal", "autocomplete": "off"}),
        help_text="Hasar, gecikme cezası, temizlik ücreti gibi durumlar için - girilirse provizyon tutarından düşülür.",
    )


class CustomerForm(forms.ModelForm):
    # Adres artık ayrı bir Address modeliyle yönetiliyor (bkz. Adresler bölümü / "Yeni Adres").
    # Bu alanlar isteğe bağlı — doldurulursa müşteriyle birlikte ilk adres de oluşturulur.
    initial_address_label = forms.CharField(
        label="Adres Etiketi", max_length=100, required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Örn. Merkez, Ev, Şube - Kadıköy"}),
    )
    initial_address_type = forms.ChoiceField(
        label="Adres Tipi", choices=Address.AddressType.choices, required=False,
        initial=Address.AddressType.FATURA, widget=forms.Select(attrs={"class": "form-select"}),
    )
    initial_address_text = forms.CharField(
        label="Adres", required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    initial_address_is_default = forms.BooleanField(
        label="Varsayılan", required=False, initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Customer
        fields = [
            "customer_type", "full_name", "tc_no", "phone", "email", "notes",
            "company_title", "tax_office", "tax_no",
            "contact_person_name", "contact_person_phone", "contact_person_email",
        ]
        widgets = {
            "customer_type": forms.Select(attrs={"class": "form-select", "id": "id_customer_type"}),
            "full_name": forms.TextInput(attrs={"class": "form-control", "id": "id_full_name"}),
            "tc_no": forms.TextInput(attrs={"class": "form-control", "maxlength": "11"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "company_title": forms.TextInput(attrs={"class": "form-control", "id": "id_company_title"}),
            "tax_office": forms.TextInput(attrs={"class": "form-control"}),
            "tax_no": forms.TextInput(attrs={"class": "form-control", "maxlength": "10"}),
            "contact_person_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person_phone": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person_email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        customer = super().save(commit=commit)
        address_text = (self.cleaned_data.get("initial_address_text") or "").strip()
        if commit and address_text:
            Address.objects.create(
                customer=customer,
                label=self.cleaned_data.get("initial_address_label") or "Adres",
                address_type=self.cleaned_data.get("initial_address_type") or Address.AddressType.FATURA,
                address=address_text,
                is_default=self.cleaned_data.get("initial_address_is_default", True),
            )
        return customer


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


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["label", "address_type", "address", "is_default"]
        widgets = {
            "label": forms.TextInput(attrs={"class": "form-control", "placeholder": "Örn. Merkez, Şube - Kadıköy"}),
            "address_type": forms.Select(attrs={"class": "form-select"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_default": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
