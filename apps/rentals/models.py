from datetime import date, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.models import SystemSettings

from .utils import turkish_upper
from .validators import validate_tax_no, validate_tc_no


class Customer(models.Model):
    class CustomerType(models.TextChoices):
        SAHIS = "SAHIS", "Şahıs"
        TUZEL = "TUZEL", "Tüzel"

    customer_number = models.CharField("Müşteri No", max_length=7, unique=True, editable=False, default="")
    customer_type = models.CharField("Müşteri Tipi", max_length=10, choices=CustomerType.choices, default=CustomerType.SAHIS)

    full_name = models.CharField("Ad Soyad / Firma Adı", max_length=150)
    tc_no = models.CharField("T.C. Kimlik No", max_length=11, blank=True, validators=[validate_tc_no])
    phone = models.CharField("Telefon", max_length=20)
    email = models.EmailField("E-posta", blank=True)
    notes = models.TextField("Notlar", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Kurumsal (Tüzel) bilgiler - sadece customer_type=TUZEL iken doldurulur
    company_title = models.CharField("Firma Unvanı", max_length=200, blank=True)
    tax_office = models.CharField("Vergi Dairesi", max_length=100, blank=True)
    tax_no = models.CharField("Vergi No", max_length=10, blank=True, validators=[validate_tax_no])
    contact_person_name = models.CharField("Yetkili Kişi Ad Soyad", max_length=150, blank=True)
    contact_person_phone = models.CharField("Yetkili Kişi Telefon", max_length=20, blank=True)
    contact_person_email = models.EmailField("Yetkili Kişi E-posta", blank=True)

    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    def clean(self):
        if self.customer_type == self.CustomerType.TUZEL and not self.company_title:
            raise ValidationError({"company_title": "Tüzel müşteriler için firma unvanı zorunludur."})

    @staticmethod
    def _generate_customer_number():
        last = (
            Customer.objects.exclude(customer_number="")
            .order_by("-customer_number")
            .values_list("customer_number", flat=True)
            .first()
        )
        sequence = int(last) + 1 if last else 1
        return f"{sequence:07d}"

    def save(self, *args, **kwargs):
        # Frontend'de zaten büyük harfe çevriliyor, backend'de de güvenlik katmanı olarak uygulanır.
        self.full_name = turkish_upper(self.full_name)
        if self.company_title:
            self.company_title = turkish_upper(self.company_title)
        if not self.customer_number:
            self.customer_number = self._generate_customer_number()
        super().save(*args, **kwargs)


class Address(models.Model):
    """Müşteriye ait fatura/teslimat adresi. Bir müşterinin birden fazla adresi olabilir."""

    class AddressType(models.TextChoices):
        FATURA = "FATURA", "Fatura"
        TESLIMAT = "TESLIMAT", "Teslimat"
        HER_IKISI = "HER_IKISI", "Her İkisi de"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses", verbose_name="Müşteri")
    label = models.CharField("Adres Etiketi", max_length=100, help_text="Örn. Merkez, Şube - Kadıköy")
    address_type = models.CharField("Adres Tipi", max_length=10, choices=AddressType.choices, default=AddressType.FATURA)
    address = models.TextField("Adres")
    is_default = models.BooleanField("Varsayılan", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Adres"
        verbose_name_plural = "Adresler"
        ordering = ["-is_default", "label"]

    def __str__(self):
        return f"{self.label} ({self.get_address_type_display()})"

    def _conflicting_types(self):
        """Aynı müşteride bu adresle aynı anda varsayılan kalamayacak tipler."""
        if self.address_type == self.AddressType.HER_IKISI:
            return [self.AddressType.FATURA, self.AddressType.TESLIMAT, self.AddressType.HER_IKISI]
        return [self.address_type, self.AddressType.HER_IKISI]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(
                customer_id=self.customer_id, is_default=True, address_type__in=self._conflicting_types()
            ).exclude(pk=self.pk).update(is_default=False)


class Driver(models.Model):
    """Aracı fiilen kullanacak kişi - fatura muhatabı olan Customer'dan ayrı bir kayıt.
    Tüzel müşterilerde personel, Şahıs müşterilerde kiralayandan farklı bir sürücü olabilir."""

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="drivers", verbose_name="İlgili Müşteri")
    full_name = models.CharField("Ad Soyad", max_length=150)
    birth_date = models.DateField("Doğum Tarihi", null=True, blank=True)
    tc_no = models.CharField("T.C. Kimlik No", max_length=11, blank=True, validators=[validate_tc_no])
    passport_no = models.CharField("Pasaport No", max_length=30, blank=True)
    address = models.TextField("İkamet Adresi", blank=True)
    phone = models.CharField("Telefon", max_length=20, blank=True)
    license_no = models.CharField("Ehliyet No", max_length=30, blank=True)
    license_class = models.CharField("Ehliyet Sınıfı", max_length=10, blank=True)
    license_issue_place = models.CharField("Ehliyetin Verildiği Yer", max_length=100, blank=True)
    license_issue_date = models.DateField("Ehliyetin Veriliş Tarihi", null=True, blank=True)
    # TODO: "Ehliyet Geçerlilik/Yenileme Tarihi" alanı ileride eklenebilir - özellikle
    # yabancı sürücülerde uluslararası ehliyetin süresi dolmuş olabiliyor. Şimdilik zorunlu değil.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sürücü"
        verbose_name_plural = "Sürücüler"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    def clean(self):
        if not self.tc_no and not self.passport_no:
            raise ValidationError("T.C. Kimlik No veya Pasaport No alanlarından en az biri girilmelidir.")


class Rental(models.Model):
    class PricingType(models.TextChoices):
        GUNLUK = "GUNLUK", "Günlük"
        AYLIK = "AYLIK", "Aylık"
        YILLIK = "YILLIK", "Yıllık"

    class Status(models.TextChoices):
        REZERVE = "REZERVE", "Rezerve"
        DEVAM_EDIYOR = "DEVAM_EDIYOR", "Devam Ediyor"
        TAMAMLANDI = "TAMAMLANDI", "Tamamlandı"
        IPTAL = "IPTAL", "İptal Edildi"

    class PaymentStatus(models.TextChoices):
        BEKLIYOR = "BEKLIYOR", "Ödeme Bekliyor"
        KISMI = "KISMI", "Kısmi Ödendi"
        ODENDI = "ODENDI", "Ödendi"

    class ProvisionType(models.TextChoices):
        YOK = "YOK", "Yok"
        EKONOMIK = "EKONOMIK", "Ekonomik"
        LUKS = "LUKS", "Lüks"

    class ProvisionStatus(models.TextChoices):
        ALINDI = "ALINDI", "Alındı"
        IADE_EDILDI = "IADE_EDILDI", "İade Edildi"
        KISMEN_KESILDI = "KISMEN_KESILDI", "Kısmen Kesildi"

    rental_no = models.CharField("Kiralama No", max_length=20, unique=True, editable=False, default="")

    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.PROTECT, related_name="rentals", verbose_name="Araç")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="rentals", verbose_name="Müşteri")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="rentals", verbose_name="Aracı Kullanacak Kişi")

    start_date = models.DateField("Başlangıç Tarihi")
    end_date = models.DateField("Planlanan Bitiş Tarihi")
    actual_end_date = models.DateField("Gerçek Teslim Tarihi", null=True, blank=True)

    pricing_type = models.CharField("Fiyatlandırma Tipi", max_length=10, choices=PricingType.choices, default=PricingType.GUNLUK)
    daily_price_snapshot = models.DecimalField("Kiralama Anındaki Günlük Fiyat", max_digits=10, decimal_places=2)
    total_price = models.DecimalField("Toplam Tutar", max_digits=10, decimal_places=2, default=0)

    status = models.CharField("Durum", max_length=20, choices=Status.choices, default=Status.REZERVE)
    payment_status = models.CharField("Ödeme Durumu", max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.BEKLIYOR)
    paid_amount = models.DecimalField("Ödenen Tutar", max_digits=10, decimal_places=2, default=0)

    delivery_km = models.PositiveIntegerField("Teslim Km", null=True, blank=True)
    return_km = models.PositiveIntegerField("İade Km", null=True, blank=True)

    provision_type = models.CharField("Provizyon Tipi", max_length=10, choices=ProvisionType.choices, default=ProvisionType.YOK)
    provision_amount = models.DecimalField(
        "Provizyon Tutarı", max_digits=10, decimal_places=2, default=0, editable=False,
        help_text="Kiralama oluşturulurken/tipi değiştiğinde ayarlardaki güncel değerden otomatik kopyalanır, sonradan ayar değişse bile sabit kalır.",
    )
    provision_status = models.CharField("Provizyon Durumu", max_length=20, choices=ProvisionStatus.choices, default=ProvisionStatus.ALINDI)
    provision_deduction_amount = models.DecimalField("Provizyon Kesinti Tutarı", max_digits=10, decimal_places=2, null=True, blank=True)
    provision_refund_date = models.DateField("Provizyon İade Tarihi", null=True, blank=True)

    notification_sent = models.BooleanField("Onay Bildirimi Gönderildi", default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_rentals")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kiralama"
        verbose_name_plural = "Kiralamalar"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.rental_no} | {self.vehicle.plate} | {self.customer.full_name} | {self.start_date} - {self.end_date}"

    @property
    def rental_days(self):
        return max((self.end_date - self.start_date).days, 1)

    @property
    def actual_rental_days(self):
        if not self.actual_end_date:
            return None
        return max((self.actual_end_date - self.start_date).days, 1)

    @property
    def provision_refund_amount(self):
        if self.provision_type == self.ProvisionType.YOK:
            return None
        return self.provision_amount - (self.provision_deduction_amount or Decimal("0"))

    @property
    def is_below_minimum_days(self):
        """Min. 3 gün kuralı - sadece uyarı amaçlı, kaydı engellemez."""
        return self.rental_days < settings.MIN_RENTAL_DAYS

    @property
    def is_payment_overdue(self):
        """Ödeme tamamlanmadan kiralama bitiş tarihi geçtiyse gecikmiş sayılır (iptal hariç)."""
        return (
            self.payment_status != self.PaymentStatus.ODENDI
            and self.status != self.Status.IPTAL
            and self.end_date < date.today()
        )

    @property
    def payment_badge_status(self):
        return "GECIKMIS" if self.is_payment_overdue else self.payment_status

    @property
    def payment_badge_label(self):
        return "Gecikmiş" if self.is_payment_overdue else self.get_payment_status_display()

    def calculate_total_price(self):
        return (self.daily_price_snapshot * self.rental_days).quantize(Decimal("0.01"))

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("Bitiş tarihi başlangıç tarihinden sonra olmalıdır.")
        if self.vehicle_id and self.start_date and self.end_date:
            if not self.vehicle.is_available_between(self.start_date, self.end_date, exclude_rental_id=self.pk):
                raise ValidationError("Seçilen araç bu tarih aralığında zaten kiralanmış/rezerve edilmiş.")

    @staticmethod
    def _generate_rental_no():
        """Yıl + o yıla ait sıra no formatında kiralama/sözleşme numarası: YYYY000000 (yıl değişince sıra sıfırlanır)"""
        year_str = str(timezone.localdate().year)
        last_no = (
            Rental.objects.filter(rental_no__startswith=year_str)
            .order_by("-rental_no")
            .values_list("rental_no", flat=True)
            .first()
        )
        sequence = int(last_no[4:]) + 1 if last_no else 0
        return f"{year_str}{sequence:06d}"

    def _refresh_provision_amount(self):
        if self.provision_type == self.ProvisionType.YOK:
            self.provision_amount = Decimal("0.00")
            return
        needs_refresh = self._state.adding
        if not needs_refresh and self.pk:
            previous_type = Rental.objects.filter(pk=self.pk).values_list("provision_type", flat=True).first()
            needs_refresh = previous_type != self.provision_type
        if needs_refresh:
            provision_settings = SystemSettings.load()
            self.provision_amount = (
                provision_settings.economy_provision_amount
                if self.provision_type == self.ProvisionType.EKONOMIK
                else provision_settings.luxury_provision_amount
            )

    def save(self, *args, **kwargs):
        if not self.total_price:
            # Kullanıcı Toplam Tutar'ı formda elle girmediyse (veya sıfır bıraktıysa) otomatik hesapla.
            # Elle girilmiş/override edilmiş bir değer varsa olduğu gibi korunur.
            self.total_price = self.calculate_total_price()
        self._refresh_provision_amount()
        is_new = self._state.adding
        if not self.rental_no:
            self.rental_no = self._generate_rental_no()
        super().save(*args, **kwargs)
        if is_new:
            RentalContract.objects.get_or_create(rental=self, defaults={"contract_no": self.rental_no})


class RentalContract(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name="contract")
    contract_no = models.CharField("Sözleşme No", max_length=50, unique=True)
    file = models.FileField("Sözleşme Dosyası", upload_to="contracts/%Y/%m/", blank=True, null=True)
    terms = models.TextField("Sözleşme Şartları", blank=True)
    signed_at = models.DateTimeField("İmza Tarihi", null=True, blank=True)

    class Meta:
        verbose_name = "Sözleşme"
        verbose_name_plural = "Sözleşmeler"

    def __str__(self):
        return self.contract_no
