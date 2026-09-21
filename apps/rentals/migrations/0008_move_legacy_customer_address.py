# Generated manually — eski tekil Customer.address alanındaki veriyi,
# alan kaldırılmadan önce yeni Address tablosuna taşır.
from django.db import migrations


def move_address(apps, schema_editor):
    Customer = apps.get_model("rentals", "Customer")
    Address = apps.get_model("rentals", "Address")

    moved = 0
    for customer in Customer.objects.exclude(address=""):
        text = (customer.address or "").strip()
        if not text:
            continue
        has_default = Address.objects.filter(
            customer_id=customer.id, is_default=True, address_type__in=["FATURA", "HER_IKISI"]
        ).exists()
        Address.objects.create(
            customer_id=customer.id,
            label="Adres",
            address_type="FATURA",
            address=text,
            is_default=not has_default,
        )
        moved += 1

    print(f"\n  [move_legacy_customer_address] {moved} müşterinin eski tekil adresi Address tablosuna taşındı.")


def reverse_move(apps, schema_editor):
    Address = apps.get_model("rentals", "Address")
    Address.objects.filter(label="Adres").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0007_remove_customer_billing_address_and_more'),
    ]

    operations = [
        migrations.RunPython(move_address, reverse_move),
    ]
