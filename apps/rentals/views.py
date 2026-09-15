import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.permissions import role_required
from apps.vehicles.models import Vehicle

from .forms import CustomerForm, DriverForm, RentalForm
from .models import Customer, Driver, Rental

MANAGE_ROLES = ["ADMIN", "OPERASYON"]
WEEKDAY_LABELS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]


@login_required
def rental_list(request):
    rentals = Rental.objects.select_related("vehicle", "customer").all()
    if request.user.is_sofor_role and not request.user.is_admin_role:
        rentals = rentals.filter(created_by=request.user)

    selected_status = request.GET.get("durum", "")
    if selected_status:
        rentals = rentals.filter(status=selected_status)

    context = {
        "rentals": rentals,
        "status_choices": Rental.Status.choices,
        "selected_status": selected_status,
    }
    context.update(_build_calendar_context(request))
    return render(request, "rentals/rental_list.html", context)


def _build_calendar_context(request):
    today = date.today()
    period = request.GET.get("periyot", "hafta")
    anchor_param = request.GET.get("baslangic")
    try:
        anchor = date.fromisoformat(anchor_param) if anchor_param else today
    except ValueError:
        anchor = today

    if period == "ay":
        range_start = anchor.replace(day=1)
        next_month = (range_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        range_end = next_month - timedelta(days=1)
        prev_start = (range_start - timedelta(days=1)).replace(day=1)
        next_start = next_month
    else:
        period = "hafta"
        range_start = anchor - timedelta(days=anchor.weekday())
        range_end = range_start + timedelta(days=6)
        prev_start = range_start - timedelta(days=7)
        next_start = range_start + timedelta(days=7)

    days = [range_start + timedelta(days=i) for i in range((range_end - range_start).days + 1)]
    day_infos = [
        {
            "date": d,
            "label": WEEKDAY_LABELS[d.weekday()],
            "is_weekend": d.weekday() >= 5,
            "is_today": d == today,
        }
        for d in days
    ]

    vehicle_status_filter = request.GET.get("arac_durum", "")
    vehicles = Vehicle.objects.exclude(status=Vehicle.Status.PASIF).order_by("plate")
    if vehicle_status_filter:
        vehicles = vehicles.filter(status=vehicle_status_filter)

    vehicle_ids = list(vehicles.values_list("id", flat=True))
    overlapping_rentals = (
        Rental.objects.select_related("vehicle", "customer")
        .filter(vehicle_id__in=vehicle_ids, start_date__lte=range_end, end_date__gte=range_start)
        .order_by("start_date")
    )

    rentals_by_vehicle = {}
    for r in overlapping_rentals:
        rentals_by_vehicle.setdefault(r.vehicle_id, []).append(r)

    total_cols = len(days)
    vehicle_rows = []
    for v in vehicles:
        v_rentals = rentals_by_vehicle.get(v.id, [])
        bars = []
        for r in v_rentals:
            bar_start = max(r.start_date, range_start)
            bar_end = min(r.end_date, range_end)
            col_start = (bar_start - range_start).days + 2
            col_end = (bar_end - range_start).days + 3
            conflict = any(
                other.pk != r.pk and other.start_date < r.end_date and other.end_date > r.start_date
                for other in v_rentals
            )
            bars.append({
                "rental": r,
                "col_start": col_start,
                "col_end": col_end,
                "conflict": conflict,
            })
        vehicle_rows.append({"vehicle": v, "bars": bars})

    return {
        "cal_period": period,
        "cal_range_start": range_start,
        "cal_range_end": range_end,
        "cal_prev_start": prev_start.isoformat(),
        "cal_next_start": next_start.isoformat(),
        "cal_days": day_infos,
        "cal_total_cols": total_cols,
        "cal_vehicle_rows": vehicle_rows,
        "cal_vehicle_status_filter": vehicle_status_filter,
        "vehicle_status_choices": Vehicle.Status.choices,
    }


@login_required
def rental_detail(request, pk):
    rental = get_object_or_404(Rental.objects.select_related("vehicle", "customer", "driver"), pk=pk)
    if request.user.is_sofor_role and not request.user.is_admin_role and rental.created_by_id != request.user.id:
        raise PermissionDenied("Bu kiralama kaydına erişim yetkiniz yok.")
    return render(request, "rentals/rental_detail.html", {
        "rental": rental,
        "min_rental_days": settings.MIN_RENTAL_DAYS,
    })


def _rental_picker_data():
    """Araç/Müşteri/Sürücü arama kutuları (searchable select) için JS'e aktarılacak veri."""
    vehicles = [
        {
            "id": v.id,
            "label": f"{v.plate} — {v.brand} {v.model_name}",
            "plate": v.plate,
            "status": v.status,
            "status_label": v.get_status_display(),
            "daily_price": str(v.daily_price),
            "estimated_return_date": v.next_maintenance_date.isoformat() if v.next_maintenance_date else None,
        }
        for v in Vehicle.objects.exclude(status=Vehicle.Status.PASIF).order_by("plate")
    ]
    customers = [
        {
            "id": c.id,
            "label": c.full_name,
            "type": c.customer_type,
            "type_label": c.get_customer_type_display(),
        }
        for c in Customer.objects.order_by("full_name")
    ]
    drivers = [
        {
            "id": d.id,
            "customer_id": d.customer_id,
            "label": d.full_name,
            "has_license": bool(d.license_no),
        }
        for d in Driver.objects.select_related("customer").order_by("full_name")
    ]
    return {
        "vehicles_json": json.dumps(vehicles),
        "customers_json": json.dumps(customers),
        "drivers_json": json.dumps(drivers),
    }


@role_required(MANAGE_ROLES)
def rental_create(request):
    if request.method == "POST":
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.created_by = request.user
            rental.save()
            messages.success(request, "Kiralama oluşturuldu.")
            return redirect("rentals:detail", pk=rental.pk)
    else:
        initial = {}
        vehicle_id = request.GET.get("arac")
        start_param = request.GET.get("baslangic")
        if vehicle_id:
            initial["vehicle"] = vehicle_id
        if start_param:
            try:
                start_date = date.fromisoformat(start_param)
                initial["start_date"] = start_date
                initial["end_date"] = start_date + timedelta(days=settings.MIN_RENTAL_DAYS)
            except ValueError:
                pass
        form = RentalForm(initial=initial)
    context = {"form": form, "title": "Yeni Kiralama"}
    context.update(_rental_picker_data())
    return render(request, "rentals/rental_form.html", context)


@role_required(MANAGE_ROLES)
def rental_update(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    if request.method == "POST":
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            messages.success(request, "Kiralama güncellendi.")
            return redirect("rentals:detail", pk=rental.pk)
    else:
        form = RentalForm(instance=rental)
    context = {"form": form, "title": "Kiralamayı Düzenle"}
    context.update(_rental_picker_data())
    return render(request, "rentals/rental_form.html", context)


@role_required(MANAGE_ROLES)
def rental_deliver(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    if request.method == "POST":
        rental.delivery_km = request.POST.get("km") or None
        rental.status = Rental.Status.DEVAM_EDIYOR
        rental.save()
        rental.vehicle.status = Vehicle.Status.KIRADA
        rental.vehicle.save(update_fields=["status"])
        messages.success(request, "Araç teslim edildi, kiralama başlatıldı.")
        return redirect("rentals:detail", pk=rental.pk)
    return render(request, "rentals/rental_action_confirm.html", {
        "rental": rental,
        "title": "Araç Teslim Et",
        "field_label": "Teslim Km",
        "current_km": rental.delivery_km,
    })


@role_required(MANAGE_ROLES)
def rental_return(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    if request.method == "POST":
        rental.return_km = request.POST.get("km") or None
        rental.status = Rental.Status.TAMAMLANDI
        rental.save()
        vehicle = rental.vehicle
        if vehicle.status == Vehicle.Status.KIRADA:
            vehicle.status = Vehicle.Status.MUSAIT
            vehicle.save(update_fields=["status"])
        messages.success(request, "Araç iade alındı, kiralama tamamlandı.")
        return redirect("rentals:detail", pk=rental.pk)
    return render(request, "rentals/rental_action_confirm.html", {
        "rental": rental,
        "title": "Araç İade Al",
        "field_label": "İade Km",
        "current_km": rental.return_km,
    })


@role_required(MANAGE_ROLES)
@require_POST
def rental_cancel(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    rental.status = Rental.Status.IPTAL
    rental.save()
    vehicle = rental.vehicle
    if vehicle.status == Vehicle.Status.KIRADA:
        vehicle.status = Vehicle.Status.MUSAIT
        vehicle.save(update_fields=["status"])
    messages.success(request, "Kiralama iptal edildi.")
    return redirect("rentals:detail", pk=rental.pk)


@role_required(MANAGE_ROLES)
def customer_list(request):
    q = request.GET.get("q", "").strip()
    customers = Customer.objects.all()
    if q:
        customers = customers.filter(
            Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(tc_no__icontains=q)
            | Q(tax_no__icontains=q) | Q(company_title__icontains=q)
        )
    return render(request, "rentals/customer_list.html", {"customers": customers, "q": q})


@role_required(MANAGE_ROLES)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    drivers = customer.drivers.all()
    rentals = customer.rentals.select_related("vehicle").order_by("-start_date")[:10]
    return render(request, "rentals/customer_detail.html", {
        "customer": customer, "drivers": drivers, "rentals": rentals,
    })


@role_required(MANAGE_ROLES)
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Müşteri eklendi.")
            return redirect("rentals:customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, "rentals/customer_form.html", {"form": form, "title": "Yeni Müşteri"})


@role_required(MANAGE_ROLES)
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Müşteri güncellendi.")
            return redirect("rentals:customer_detail", pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, "rentals/customer_form.html", {"form": form, "title": "Müşteriyi Düzenle"})


@role_required(MANAGE_ROLES)
def customer_duplicate_check(request):
    tc_no = request.GET.get("tc_no", "").strip()
    tax_no = request.GET.get("tax_no", "").strip()
    exclude_pk = request.GET.get("exclude", "")

    qs = Customer.objects.all()
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)

    match = None
    if tc_no:
        match = qs.filter(tc_no=tc_no).first()
    elif tax_no:
        match = qs.filter(tax_no=tax_no).first()

    if match:
        return JsonResponse({"exists": True, "name": match.full_name, "id": match.pk})
    return JsonResponse({"exists": False})


@role_required(MANAGE_ROLES)
def driver_create(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == "POST":
        form = DriverForm(request.POST)
        if form.is_valid():
            driver = form.save(commit=False)
            driver.customer = customer
            driver.save()
            messages.success(request, "Sürücü eklendi.")
            return redirect("rentals:customer_detail", pk=customer.pk)
    else:
        form = DriverForm()
    return render(request, "rentals/driver_form.html", {
        "form": form, "title": "Yeni Sürücü", "customer": customer,
    })


@role_required(MANAGE_ROLES)
def driver_update(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == "POST":
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            messages.success(request, "Sürücü güncellendi.")
            return redirect("rentals:customer_detail", pk=driver.customer_id)
    else:
        form = DriverForm(instance=driver)
    return render(request, "rentals/driver_form.html", {
        "form": form, "title": "Sürücüyü Düzenle", "customer": driver.customer,
    })


@role_required(MANAGE_ROLES)
@require_POST
def driver_quick_create(request, customer_pk):
    """Yeni Kiralama formundan sayfa yenilenmeden hızlı sürücü ekleme (AJAX)."""
    customer = get_object_or_404(Customer, pk=customer_pk)
    form = DriverForm(request.POST)
    if form.is_valid():
        driver = form.save(commit=False)
        driver.customer = customer
        driver.save()
        return JsonResponse({
            "id": driver.pk,
            "label": driver.full_name,
            "has_license": bool(driver.license_no),
        })
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
