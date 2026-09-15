from django.contrib import admin
from .models import Damage

@admin.register(Damage)
class DamageAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "status", "reported_date", "reported_by", "repair_cost")
    list_filter = ("status",)
    search_fields = ("vehicle__plate",)
