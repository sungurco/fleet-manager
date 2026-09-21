from django.db import models


class SystemSettings(models.Model):
    """Tek satırlık genel sistem ayarları (singleton). SystemSettings.load() ile erişilir."""

    economy_provision_amount = models.DecimalField(
        "Ekonomik Sınıf Provizyon Tutarı", max_digits=10, decimal_places=2, default=5000
    )
    luxury_provision_amount = models.DecimalField(
        "Lüks Sınıf Provizyon Tutarı", max_digits=10, decimal_places=2, default=10000
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sistem Ayarları"
        verbose_name_plural = "Sistem Ayarları"

    def __str__(self):
        return "Sistem Ayarları"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
