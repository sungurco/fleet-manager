"""
Yerel/test ortamında canlı deneme için örnek veri oluşturur: Admin + Operasyon
kullanıcısı, birkaç araç, birkaç müşteri, provizyonlu ve provizyonsuz birer
kiralama kaydı. Idempotent'tir (get_or_create) - tekrar çalıştırmak güvenlidir.

Kullanım: python manage.py seed_demo_data
"""
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.common.models import SystemSettings
from apps.rentals.models import Customer, Rental
from apps.rentals.utils import turkish_upper
from apps.vehicles.models import Vehicle

DEMO_PASSWORD = "Demo12345!"


class Command(BaseCommand):
    help = "Canlı test için örnek kullanıcı ve veri oluşturur (idempotent)."

    def handle(self, *args, **options):
        SystemSettings.load()

        admin, created = User.objects.get_or_create(
            username="demo_admin", defaults={"role": User.Role.ADMIN, "email": "demo_admin@example.com"}
        )
        admin.role = User.Role.ADMIN
        admin.set_password(DEMO_PASSWORD)
        admin.save()
        self.stdout.write(self.style.SUCCESS(f"{'Oluşturuldu' if created else 'Güncellendi'}: demo_admin / {DEMO_PASSWORD} (Admin)"))

        operasyon, created = User.objects.get_or_create(
            username="demo_operasyon", defaults={"role": User.Role.OPERASYON, "email": "demo_operasyon@example.com"}
        )
        operasyon.role = User.Role.OPERASYON
        operasyon.set_password(DEMO_PASSWORD)
        operasyon.save()
        self.stdout.write(self.style.SUCCESS(f"{'Oluşturuldu' if created else 'Güncellendi'}: demo_operasyon / {DEMO_PASSWORD} (Operasyon)"))

        vehicle_musait, _ = Vehicle.objects.get_or_create(
            plate="34DEMO01",
            defaults=dict(brand="Renault", model_name="Clio", year=2023, color=Vehicle.Color.BEYAZ, status=Vehicle.Status.MUSAIT),
        )
        vehicle_kirada, _ = Vehicle.objects.get_or_create(
            plate="34DEMO02",
            defaults=dict(brand="Volkswagen", model_name="Passat", year=2022, color=Vehicle.Color.SIYAH, status=Vehicle.Status.MUSAIT),
        )

        # Customer.save() isimleri Türkçe büyük harfe normalize eder (bkz. apps/rentals/utils.turkish_upper);
        # get_or_create'in tekrar çalıştırıldığında aynı kaydı bulabilmesi için lookup değeri de normalize edilir.
        customer1, _ = Customer.objects.get_or_create(
            full_name=turkish_upper("Ahmet Demo Yılmaz"),
            defaults=dict(phone="5551234567", customer_type=Customer.CustomerType.SAHIS),
        )
        customer2, _ = Customer.objects.get_or_create(
            full_name=turkish_upper("Demo Lojistik A.Ş."),
            defaults=dict(phone="5559876543", customer_type=Customer.CustomerType.TUZEL, company_title=turkish_upper("Demo Lojistik A.Ş.")),
        )

        # Provizyonsuz, devam eden kiralama (34DEMO02'yi Kirada yapar)
        rental_no_provision, created = Rental.objects.get_or_create(
            vehicle=vehicle_kirada, customer=customer1,
            defaults=dict(
                start_date=date.today() - timedelta(days=2),
                end_date=date.today() + timedelta(days=5),
                daily_price_snapshot=Decimal("1500.00"),
                status=Rental.Status.DEVAM_EDIYOR,
                provision_type=Rental.ProvisionType.YOK,
            ),
        )
        if created:
            vehicle_kirada.status = Vehicle.Status.KIRADA
            vehicle_kirada.save(update_fields=["status"])

        # Provizyonlu (Lüks) rezerve kiralama - 34DEMO01 Müsait kalır
        rental_with_provision, _ = Rental.objects.get_or_create(
            vehicle=vehicle_musait, customer=customer2,
            defaults=dict(
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=8),
                daily_price_snapshot=Decimal("2500.00"),
                status=Rental.Status.REZERVE,
                provision_type=Rental.ProvisionType.LUKS,
            ),
        )

        self.stdout.write(self.style.SUCCESS(
            f"Örnek veri hazır: {vehicle_musait} (Müsait), {vehicle_kirada} (Kirada), "
            f"{customer1}, {customer2}, kiralama #{rental_no_provision.rental_no} (provizyonsuz), "
            f"kiralama #{rental_with_provision.rental_no} (Lüks provizyonlu)."
        ))
