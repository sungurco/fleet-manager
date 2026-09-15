from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import role_required
from apps.rentals.models import Rental

from .forms import VehicleForm
from .models import Vehicle

MANAGE_ROLES = ["ADMIN", "OPERASYON"]


def _driver_vehicle_queryset(user):
    return Vehicle.objects.filter(rentals__created_by=user).distinct()


@login_required
def vehicle_list(request):
    if request.user.is_sofor_role and not request.user.is_admin_role:
        vehicles = _driver_vehicle_queryset(request.user)
    else:
        vehicles = Vehicle.objects.all()
    vehicles = vehicles.select_related("inspection")

    status_filter = request.GET.get("durum", "")
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)

    return render(request, "vehicles/vehicle_list.html", {
        "vehicles": vehicles,
        "status_choices": Vehicle.Status.choices,
        "selected_status": status_filter,
    })


@login_required
def vehicle_detail(request, pk):
    if request.user.is_sofor_role and not request.user.is_admin_role:
        vehicle = get_object_or_404(_driver_vehicle_queryset(request.user), pk=pk)
    else:
        vehicle = get_object_or_404(Vehicle, pk=pk)

    rentals = Rental.objects.filter(vehicle=vehicle).select_related("customer").order_by("-start_date")
    return render(request, "vehicles/vehicle_detail.html", {"vehicle": vehicle, "rentals": rentals})


@role_required(MANAGE_ROLES)
def vehicle_create(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, "Araç eklendi.")
            return redirect("vehicles:detail", pk=vehicle.pk)
    else:
        form = VehicleForm()
    return render(request, "vehicles/vehicle_form.html", {"form": form, "title": "Yeni Araç"})


@role_required(MANAGE_ROLES)
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Araç güncellendi.")
            return redirect("vehicles:detail", pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, "vehicles/vehicle_form.html", {"form": form, "title": "Aracı Düzenle"})
