from django.contrib import admin
from .models import Address, Customer, Driver, Rental, RentalContract


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_number", "full_name", "customer_type", "phone", "email", "tc_no", "tax_no")
    list_filter = ("customer_type",)
    search_fields = ("customer_number", "full_name", "phone", "tc_no", "tax_no", "company_title")


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("full_name", "customer", "tc_no", "passport_no", "license_no")
    search_fields = ("full_name", "tc_no", "passport_no", "license_no", "customer__full_name")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("label", "customer", "address_type", "is_default")
    list_filter = ("address_type", "is_default")
    search_fields = ("label", "customer__full_name")


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("rental_no", "vehicle", "customer", "start_date", "end_date", "status", "payment_status", "total_price", "provision_type", "provision_status")
    list_filter = ("status", "payment_status", "pricing_type", "provision_type", "provision_status")
    search_fields = ("rental_no", "vehicle__plate", "customer__full_name")
    date_hierarchy = "start_date"


@admin.register(RentalContract)
class RentalContractAdmin(admin.ModelAdmin):
    list_display = ("contract_no", "rental", "signed_at")
