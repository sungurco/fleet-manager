from django.contrib import admin
from .models import HGSExpense

@admin.register(HGSExpense)
class HGSExpenseAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "date", "amount", "location", "entered_by")
    list_filter = ("date",)
    search_fields = ("vehicle__plate",)
