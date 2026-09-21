from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse

from apps.damages.models import Damage
from apps.maintenance.models import Inspection
from apps.rentals.models import Rental
from apps.vehicles.models import Vehicle


@login_required
def dashboard(request):
    if request.user.is_sofor_role and not request.user.is_admin_role:
        return _driver_dashboard(request)
    return _operations_dashboard(request)


def _driver_dashboard(request):
    context = {
        "my_rentals": Rental.objects.filter(
            vehicle__rentals__created_by=request.user, status=Rental.Status.DEVAM_EDIYOR
        ).select_related("vehicle", "customer"),
    }
    return render(request, "dashboard_sofor.html", context)


def _operations_dashboard(request):
    today = date.today()
    inspection_horizon = today + timedelta(days=30)
    contract_horizon = today + timedelta(days=10)

    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(status=Vehicle.Status.MUSAIT).count()
    rented_vehicles = Vehicle.objects.filter(status=Vehicle.Status.KIRADA).count()
    service_vehicles = Vehicle.objects.filter(status=Vehicle.Status.SERVISTE).count()
    damaged_vehicles = Vehicle.objects.filter(status=Vehicle.Status.HASARLI).count()
    passive_vehicles = Vehicle.objects.filter(status=Vehicle.Status.PASIF).count()

    occupancy_base = max(total_vehicles, 1)
    occupancy = {
        "available": available_vehicles,
        "rented": rented_vehicles,
        "service": service_vehicles,
        "damaged": damaged_vehicles,
        "available_pct": round(available_vehicles * 100 / occupancy_base),
        "rented_pct": round(rented_vehicles * 100 / occupancy_base),
        "service_pct": round(service_vehicles * 100 / occupancy_base),
        "damaged_pct": round(damaged_vehicles * 100 / occupancy_base),
    }
    # CSS conic-gradient stop offsets (cumulative percentages)
    occupancy["rented_stop"] = occupancy["rented_pct"]
    occupancy["service_stop"] = occupancy["rented_stop"] + occupancy["service_pct"]
    occupancy["damaged_stop"] = occupancy["service_stop"] + occupancy["damaged_pct"]

    active_billable = Rental.objects.filter(status__in=[Rental.Status.DEVAM_EDIYOR, Rental.Status.TAMAMLANDI])

    this_month_paid = (
        active_billable.filter(updated_at__year=today.year, updated_at__month=today.month)
        .aggregate(total=Sum("paid_amount"))["total"]
        or 0
    )
    last_month = (today.replace(day=1) - timedelta(days=1))
    last_month_paid = (
        active_billable.filter(updated_at__year=last_month.year, updated_at__month=last_month.month)
        .aggregate(total=Sum("paid_amount"))["total"]
        or 0
    )
    revenue_trend = None
    if last_month_paid:
        revenue_trend = round((float(this_month_paid) - float(last_month_paid)) * 100 / float(last_month_paid))

    pending_collection = sum(
        (r.total_price - r.paid_amount)
        for r in Rental.objects.filter(
            status__in=[Rental.Status.REZERVE, Rental.Status.DEVAM_EDIYOR, Rental.Status.TAMAMLANDI]
        ).exclude(payment_status=Rental.PaymentStatus.ODENDI)
    )

    attention_items = []
    for insp in Inspection.objects.select_related("vehicle").filter(
        next_inspection_date__gte=today, next_inspection_date__lte=inspection_horizon
    ).order_by("next_inspection_date")[:6]:
        days_left = (insp.next_inspection_date - today).days
        attention_items.append({
            "severity": "high" if days_left <= 7 else "medium",
            "title": f"{insp.vehicle.plate} — muayene tarihi yaklaşıyor",
            "meta": f"{insp.vehicle.brand} {insp.vehicle.model_name}",
            "days_left": days_left,
            "url": reverse("admin:maintenance_inspection_change", args=[insp.pk]),
        })

    for r in Rental.objects.select_related("vehicle", "customer").filter(
        status=Rental.Status.DEVAM_EDIYOR, end_date__gte=today, end_date__lte=contract_horizon
    ).order_by("end_date")[:6]:
        days_left = (r.end_date - today).days
        attention_items.append({
            "severity": "high" if days_left <= 2 else "medium",
            "title": f"{r.vehicle.plate} — sözleşme bitiyor",
            "meta": r.customer.full_name,
            "days_left": days_left,
            "url": reverse("rentals:detail", args=[r.pk]),
        })

    for r in Rental.objects.select_related("vehicle", "customer").filter(
        status__in=[Rental.Status.DEVAM_EDIYOR, Rental.Status.TAMAMLANDI]
    ).exclude(payment_status=Rental.PaymentStatus.ODENDI).order_by("-start_date")[:6]:
        attention_items.append({
            "severity": "high",
            "title": f"{r.vehicle.plate} — tahsilat bekliyor",
            "meta": f"{r.customer.full_name} · {(r.total_price - r.paid_amount):.0f} TL",
            "days_left": None,
            "url": reverse("rentals:detail", args=[r.pk]),
        })

    attention_items.sort(key=lambda i: (i["days_left"] is None, i["days_left"] if i["days_left"] is not None else 0))

    recent_rentals = Rental.objects.select_related("vehicle", "customer").order_by("-created_at")[:5]

    context = {
        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "rented_vehicles": rented_vehicles,
        "service_vehicles": service_vehicles,
        "damaged_vehicles": damaged_vehicles,
        "passive_vehicles": passive_vehicles,
        "occupancy": occupancy,
        "this_month_paid": this_month_paid,
        "revenue_trend": revenue_trend,
        "pending_collection": pending_collection,
        "attention_items": attention_items[:8],
        "recent_rentals": recent_rentals,
        "open_damages": Damage.objects.filter(status__in=[Damage.Status.ACIK, Damage.Status.SERVISTE]).count(),
    }
    return render(request, "dashboard.html", context)
