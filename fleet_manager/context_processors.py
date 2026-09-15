from datetime import date, timedelta

from django.urls import reverse


def alerts(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    if user.is_sofor_role and not user.is_admin_role:
        return {}

    from apps.maintenance.models import Inspection
    from apps.rentals.models import Rental

    today = date.today()
    inspection_horizon = today + timedelta(days=15)
    contract_horizon = today + timedelta(days=7)

    inspections = list(
        Inspection.objects.select_related("vehicle")
        .filter(next_inspection_date__gte=today, next_inspection_date__lte=inspection_horizon)
        .order_by("next_inspection_date")[:5]
    )
    ending_rentals = list(
        Rental.objects.select_related("vehicle", "customer")
        .filter(status=Rental.Status.DEVAM_EDIYOR, end_date__gte=today, end_date__lte=contract_horizon)
        .order_by("end_date")[:5]
    )
    unpaid_rentals = list(
        Rental.objects.select_related("vehicle", "customer")
        .filter(status__in=[Rental.Status.DEVAM_EDIYOR, Rental.Status.TAMAMLANDI])
        .exclude(payment_status=Rental.PaymentStatus.ODENDI)
        .order_by("-start_date")[:5]
    )

    items = []
    for insp in inspections:
        days_left = (insp.next_inspection_date - today).days
        items.append({
            "severity": "high" if days_left <= 7 else "medium",
            "title": f"{insp.vehicle.plate} muayenesi yaklaşıyor",
            "meta": f"{days_left} gün kaldı",
            "url": reverse("admin:maintenance_inspection_change", args=[insp.pk]),
        })
    for r in ending_rentals:
        days_left = (r.end_date - today).days
        items.append({
            "severity": "high" if days_left <= 2 else "medium",
            "title": f"{r.vehicle.plate} sözleşmesi bitiyor",
            "meta": f"{r.customer.full_name} · {days_left} gün kaldı",
            "url": reverse("rentals:detail", args=[r.pk]),
        })
    for r in unpaid_rentals:
        remaining = r.total_price - r.paid_amount
        items.append({
            "severity": "high",
            "title": f"{r.vehicle.plate} tahsilatı bekliyor",
            "meta": f"{r.customer.full_name} · {remaining:.0f} TL",
            "url": reverse("rentals:detail", args=[r.pk]),
        })

    return {
        "global_alerts": items[:8],
        "global_alerts_count": len(inspections) + len(ending_rentals) + len(unpaid_rentals),
    }
