"""
Yaklaşan muayene / bakım / sözleşme bitişleri için otomatik e-posta uyarıları.
Celery Beat ile her gün 08:00'de çalışır (bkz. fleet_manager/celery.py).
Eşik değerleri: settings.NOTIFICATION_THRESHOLDS_DAYS (varsayılan: 30, 15, 7 gün)
"""
from datetime import date, timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from apps.maintenance.models import Inspection, Maintenance
from apps.rentals.models import Rental


def _get_admin_operasyon_emails():
    from apps.accounts.models import User
    return list(
        User.objects.filter(role__in=[User.Role.ADMIN, User.Role.OPERASYON], is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )


@shared_task
def send_expiry_notifications():
    today = date.today()
    thresholds = settings.NOTIFICATION_THRESHOLDS_DAYS
    recipients = _get_admin_operasyon_emails()
    if not recipients:
        return "Alıcı e-posta adresi bulunamadı."

    lines = []

    # Muayene tarihleri
    for days in thresholds:
        target = today + timedelta(days=days)
        for insp in Inspection.objects.filter(next_inspection_date=target):
            lines.append(f"[MUAYENE] {insp.vehicle.plate} - {insp.next_inspection_date} ({days} gün kaldı)")

    # Bakım tarihleri
    for days in thresholds:
        target = today + timedelta(days=days)
        for m in Maintenance.objects.filter(next_due_date=target):
            lines.append(f"[BAKIM] {m.vehicle.plate} - {m.next_due_date} ({days} gün kaldı)")

    # Sözleşme / kiralama bitişleri
    for days in thresholds:
        target = today + timedelta(days=days)
        for r in Rental.objects.filter(end_date=target, status=Rental.Status.DEVAM_EDIYOR):
            lines.append(f"[SÖZLEŞME BİTİŞİ] {r.vehicle.plate} - {r.customer.full_name} - {r.end_date} ({days} gün kaldı)")

    if not lines:
        return "Bugün için uyarı bulunamadı."

    send_mail(
        subject=f"Filo Yönetimi - Günlük Uyarı Raporu ({today})",
        message="\n".join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
    )
    return f"{len(lines)} uyarı gönderildi."
