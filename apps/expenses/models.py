from django.db import models


class HGSExpense(models.Model):
    """HGS harcamaları - personel tarafından manuel girilir."""
    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE, related_name="hgs_expenses", verbose_name="Araç")
    rental = models.ForeignKey("rentals.Rental", on_delete=models.SET_NULL, null=True, blank=True, related_name="hgs_expenses", verbose_name="İlgili Kiralama")
    date = models.DateField("Tarih")
    amount = models.DecimalField("Tutar", max_digits=10, decimal_places=2)
    location = models.CharField("Geçiş Noktası", max_length=100, blank=True)
    notes = models.CharField("Not", max_length=200, blank=True)
    entered_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="entered_hgs")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "HGS Harcaması"
        verbose_name_plural = "HGS Harcamaları"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.vehicle.plate} - {self.date} - {self.amount} TL"
