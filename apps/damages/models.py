from django.db import models


class Damage(models.Model):
    class Status(models.TextChoices):
        ACIK = "ACIK", "Açık"
        SERVISTE = "SERVISTE", "Serviste"
        KAPALI = "KAPALI", "Kapatıldı"

    class ReportedByRole(models.TextChoices):
        SOFOR = "SOFOR", "Şoför"
        OPERASYON = "OPERASYON", "Operasyon"
        ADMIN = "ADMIN", "Admin"

    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE, related_name="damages", verbose_name="Araç")
    rental = models.ForeignKey("rentals.Rental", on_delete=models.SET_NULL, null=True, blank=True, related_name="damages", verbose_name="İlgili Kiralama")
    reported_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="reported_damages")
    reported_date = models.DateField("Bildirim Tarihi", auto_now_add=True)
    description = models.TextField("Hasar Açıklaması")
    photo = models.ImageField("Fotoğraf", upload_to="damages/%Y/%m/", blank=True, null=True)
    repair_cost = models.DecimalField("Onarım Maliyeti", max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField("Durum", max_length=20, choices=Status.choices, default=Status.ACIK)
    resolved_date = models.DateField("Kapatılma Tarihi", null=True, blank=True)

    class Meta:
        verbose_name = "Hasar Kaydı"
        verbose_name_plural = "Hasar Kayıtları"
        ordering = ["-reported_date"]

    def __str__(self):
        return f"{self.vehicle.plate} - {self.get_status_display()} ({self.reported_date})"
