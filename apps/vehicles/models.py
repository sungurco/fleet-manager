from django.db import models


class Vehicle(models.Model):
    class Status(models.TextChoices):
        MUSAIT = "MUSAIT", "Müsait"
        KIRADA = "KIRADA", "Kirada"
        SERVISTE = "SERVISTE", "Serviste"
        HASARLI = "HASARLI", "Hasarlı"
        PASIF = "PASIF", "Pasif / Filodan Çıkarıldı"

    class Color(models.TextChoices):
        BEYAZ = "BEYAZ", "Beyaz"
        SIYAH = "SIYAH", "Siyah"
        GRI = "GRI", "Gri"
        GUMUS = "GUMUS", "Gümüş"
        KIRMIZI = "KIRMIZI", "Kırmızı"
        MAVI = "MAVI", "Mavi"
        LACIVERT = "LACIVERT", "Lacivert"
        YESIL = "YESIL", "Yeşil"
        SARI = "SARI", "Sarı"
        TURUNCU = "TURUNCU", "Turuncu"
        KAHVERENGI = "KAHVERENGI", "Kahverengi"
        BORDO = "BORDO", "Bordo"
        BEJ = "BEJ", "Bej"
        TURKUAZ = "TURKUAZ", "Turkuaz"
        MOR = "MOR", "Mor"
        ALTIN = "ALTIN", "Altın"
        DIGER = "DIGER", "Diğer"

    plate = models.CharField("Plaka", max_length=20, unique=True)
    brand = models.CharField("Marka", max_length=50)
    model_name = models.CharField("Model", max_length=50)
    year = models.PositiveIntegerField("Model Yılı")
    color = models.CharField("Renk", max_length=30, choices=Color.choices, blank=True)
    chassis_no = models.CharField("Şasi No", max_length=50, blank=True)
    engine_no = models.CharField("Motor No", max_length=50, blank=True)
    fuel_type = models.CharField("Yakıt Tipi", max_length=30, blank=True)
    transmission = models.CharField("Vites Tipi", max_length=30, blank=True)
    km = models.PositiveIntegerField("Kilometre", default=0)

    daily_price = models.DecimalField(
        "Günlük Fiyat", max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="DEPRECATED: artık her kiralamada elle girilir, araç kaydında kullanılmıyor.",
    )
    monthly_price = models.DecimalField("Aylık Fiyat", max_digits=10, decimal_places=2, null=True, blank=True)
    yearly_price = models.DecimalField("Yıllık Fiyat", max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField("Durum", max_length=20, choices=Status.choices, default=Status.MUSAIT)

    purchase_date = models.DateField("Filoya Katılım Tarihi", null=True, blank=True)
    acquisition_date = models.DateField("Satın Alma Tarihi", null=True, blank=True)
    purchase_cost = models.DecimalField("Satın Alma Maliyeti", max_digits=12, decimal_places=2, null=True, blank=True)
    next_maintenance_date = models.DateField(
        "Sonraki Bakım Tarihi", null=True, blank=True,
        help_text="DEPRECATED: bakım takibi ileride ayrı bir Bakım modülü altında ele alınacak, formdan kaldırıldı.",
    )
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
