from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Rol tabanlı özel kullanıcı modeli.
    Roller: Admin (birden fazla olabilir), Operasyon, Şoför
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        OPERASYON = "OPERASYON", "Operasyon"
        SOFOR = "SOFOR", "Şoför"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OPERASYON)
    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_operasyon_role(self):
        return self.role == self.Role.OPERASYON

    @property
    def is_sofor_role(self):
        return self.role == self.Role.SOFOR

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
