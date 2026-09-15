from django.db import models


class Maintenance(models.Model):
    class Type(models.TextChoices):
        PERIYODIK = "PERIYODIK", "Periyodik Bakım"
        ARIZA = "ARIZA", "Arıza Onarımı"
        LASTIK = "LASTIK", "Lastik Değişimi"
        DIGER = "DIGER", "Diğer"

    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE, related_name="maintenances", verbose_name="Araç")
    type = models.CharField("Tür", max_length=20, choices=Type.choices, default=Type.PERIYODIK)
    service_date = models.DateField("Servis Tarihi")
    next_due_date = models.DateField("Bir Sonraki Bakım Tarihi", null=True, blank=True)
    next_due_km = models.PositiveIntegerField("Bir Sonraki Bakım Km", null=True, blank=True)
    cost = models.DecimalField("Maliyet", max_digits=10, decimal_places=2, default=0)
    service_provider = models.CharField("Servis/Yetkili Bayi", max_length=100, blank=True)
    description = models.TextField("Açıklama", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bakım Kaydı"
        verbose_name_plural = "Bakım Kayıtları"
        ordering = ["-service_date"]

    def __str__(self):
        return f"{self.vehicle.plate} - {self.get_type_display()} ({self.service_date})"


class Inspection(models.Model):
    """Araç muayene takibi."""
    vehicle = models.OneToOneField("vehicles.Vehicle", on_delete=models.CASCADE, related_name="inspection", verbose_name="Araç")
    last_inspection_date = models.DateField("Son Muayene Tarihi")
    next_inspection_date = models.DateField("Bir Sonraki Muayene Tarihi")
    notes = models.TextField("Notlar", blank=True)

    class Meta:
        verbose_name = "Muayene Kaydı"
        verbose_name_plural = "Muayene Kayıtları"
        ordering = ["next_inspection_date"]

    def __str__(self):
        return f"{self.vehicle.plate} - Sonraki Muayene: {self.next_inspection_date}"
