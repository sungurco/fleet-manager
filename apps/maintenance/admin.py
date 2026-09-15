from django.contrib import admin
from .models import Maintenance, Inspection

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "type", "service_date", "next_due_date", "cost")
    list_filter = ("type",)
    search_fields = ("vehicle__plate",)

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "last_inspection_date", "next_inspection_date")
    ordering = ("next_inspection_date",)
