from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    path("doluluk/", views.occupancy_report, name="occupancy"),
    path("finansal/", views.financial_report, name="financial"),
    path("bakim-muayene/", views.maintenance_report, name="maintenance"),
    path("hgs/", views.hgs_report, name="hgs"),
    path("hasar/", views.damage_report, name="damage"),
]
