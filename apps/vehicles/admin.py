from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate", "brand", "model_name", "year", "status", "daily_price", "km")
    list_filter = ("status", "brand", "fuel_type")
    search_fields = ("plate", "brand", "model_name", "chassis_no")
