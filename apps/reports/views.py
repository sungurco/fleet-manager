from datetime import date

from django.db.models import Sum, Count
from django.shortcuts import render

from apps.accounts.permissions import role_required
from apps.common.sorting import apply_sort_to_list
from apps.damages.models import Damage
from apps.expenses.models import HGSExpense
from apps.maintenance.models import Inspection, Maintenance
from apps.rentals.models import Rental
from apps.vehicles.models import Vehicle
from .exporters import export_to_excel


@role_required(["ADMIN", "OPERASYON"])
def occupancy_report(request):
    """Filo doluluk raporu: her araç için toplam kiralanan gün sayısı."""
    vehicles = Vehicle.objects.all()
    table_rows = []
    for v in vehicles:
        rented_days = sum(r.rental_days for r in v.rentals.filter(status__in=["DEVAM_EDIYOR", "TAMAMLANDI"]))
        table_rows.append({"vehicle": v, "rented_days": rented_days})

    sort_map = {
        "plaka": lambda row: row["vehicle"].plate,
        "marka": lambda row: row["vehicle"].brand,
        "model": lambda row: row["vehicle"].model_name,
        "durum": lambda row: row["vehicle"].status,
        "gun": lambda row: row["rented_days"],
    }
    table_rows, sort_context = apply_sort_to_list(request, table_rows, sort_map)

    if request.GET.get("export") == "excel":
        rows = [[r["vehicle"].plate, r["vehicle"].brand, r["vehicle"].model_name, r["vehicle"].get_status_display(), r["rented_days"]] for r in table_rows]
        return export_to_excel("doluluk_raporu", ["Plaka", "Marka", "Model", "Durum", "Kiralanan Gün"], rows)

    context = {"table_rows": table_rows}
    context.update(sort_context)
    return render(request, "reports/occupancy_report.html", context)


@role_required(["ADMIN", "OPERASYON"])
def financial_report(request):
    """Dönemsel gelir ve araç bazlı kârlılık raporu."""
    rentals = Rental.objects.filter(status__in=["DEVAM_EDIYOR", "TAMAMLANDI"])
    total_income = rentals.aggregate(total=Sum("total_price"))["total"] or 0
    by_vehicle = (
        rentals.values("vehicle__plate")
        .annotate(income=Sum("total_price"), rental_count=Count("id"))
        .order_by("-income")
    )

    if request.GET.get("export") == "excel":
        rows = [[r["vehicle__plate"], r["rental_count"], r["income"]] for r in by_vehicle]
        return export_to_excel("finansal_rapor", ["Plaka", "Kiralama Sayısı", "Gelir"], rows)

    return render(
        request,
        "reports/financial_report.html",
        {"total_income": total_income, "by_vehicle": by_vehicle},
    )


@role_required(["ADMIN", "OPERASYON"])
def maintenance_report(request):
    """Yaklaşan muayene ve bakım tarihleri."""
    today = date.today()
    inspections = Inspection.objects.filter(next_inspection_date__gte=today).order_by("next_inspection_date")
    maintenances = Maintenance.objects.filter(next_due_date__gte=today).order_by("next_due_date")
    return render(
        request,
        "reports/maintenance_report.html",
        {"inspections": inspections, "maintenances": maintenances},
    )


@role_required(["ADMIN", "OPERASYON"])
def hgs_report(request):
    expenses = HGSExpense.objects.select_related("vehicle").order_by("-date")
    total = expenses.aggregate(total=Sum("amount"))["total"] or 0

    if request.GET.get("export") == "excel":
        rows = [[e.vehicle.plate, e.date, e.amount, e.location] for e in expenses]
        return export_to_excel("hgs_raporu", ["Plaka", "Tarih", "Tutar", "Geçiş Noktası"], rows)

    return render(request, "reports/hgs_report.html", {"expenses": expenses, "total": total})


@role_required(["ADMIN", "OPERASYON"])
def damage_report(request):
    damages = Damage.objects.select_related("vehicle").order_by("-reported_date")
    return render(request, "reports/damage_report.html", {"damages": damages})
