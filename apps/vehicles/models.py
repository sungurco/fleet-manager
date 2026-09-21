from django.db import models


class Vehicle(models.Model):
    class Status(models.TextChoices):
        MUSAIT = "MUSAIT", "Müsait"
        KIRADA = "KIRADA", "Kirada"
        SERVISTE = "SERVISTE", "Serviste"
        HASARLI = "HASARLI", "Hasarlı"
        PASIF = "PASIF", "Pasif / Filodan Çıkarıldı"

    plate = models.CharField("Plaka", max_length=20, unique=True)
    brand = models.CharField("Marka", max_length=50)
    model_name = models.CharField("Model", max_length=50)
    year = models.PositiveIntegerField("Model Yılı")
    color = models.CharField("Renk", max_length=30, blank=True)
    chassis_no = models.CharField("Şasi No", max_length=50, blank=True)
    engine_no = models.CharField("Motor No", max_length=50, blank=True)
    fuel_type = models.CharField("Yakıt Tipi", max_length=30, blank=True)
    transmission = models.CharField("Vites Tipi", max_length=30, blank=True)
    km = models.PositiveIntegerField("Kilometre", default=0)

    daily_price = models.DecimalField("Günlük Fiyat", max_digits=10, decimal_places=2)
    monthly_price = models.DecimalField("Aylık Fiyat", max_digits=10, decimal_places=2, null=True, blank=True)
    yearly_price = models.DecimalField("Yıllık Fiyat", max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField("Durum", max_length=20, choices=Status.choices, default=Status.MUSAIT)

    purchase_date = models.DateField("Filoya Katılım Tarihi", null=True, blank=True)
    next_maintenance_date = models.DateField("Sonraki Bakım Tarihi", null=True, blank=True)
    estimated_service_end_date = models.DateField(
        "Tahmini Servis Bitiş Tarihi", null=True, blank=True,
        help_text="Araç Serviste iken bu bakımın ne zaman biteceğini belirtir.",
    )
    estimated_resolution_date = models.DateField(
        "Tahmini Çözüm Tarihi", null=True, blank=True,
        help_text="Hasarlı araçlar için opsiyonel — süreç genelde belirsizdir.",
    )
    fleet_contract_end_date = models.DateField("Filo Sözleşme Bitiş Tarihi", null=True, blank=True)
    notes = models.TextField("Notlar", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Araç"
        verbose_name_plural = "Araçlar"
        ordering = ["plate"]

    def __str__(self):
        return f"{self.plate} - {self.brand} {self.model_name}"

    def is_available_between(self, start_date, end_date, exclude_rental_id=None):
        """Belirtilen tarih aralığında araç müsait mi kontrol eder (çakışma kontrolü)."""
        from apps.rentals.models import Rental

        overlapping = Rental.objects.filter(
            vehicle=self,
            status__in=[Rental.Status.REZERVE, Rental.Status.DEVAM_EDIYOR],
            start_date__lt=end_date,
            end_date__gt=start_date,
        )
        if exclude_rental_id:
            overlapping = overlapping.exclude(pk=exclude_rental_id)
        return not overlapping.exists()
