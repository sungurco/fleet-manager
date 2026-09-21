from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("hesap/", include("apps.accounts.urls")),
    path("araclar/", include("apps.vehicles.urls")),
    path("kiralama/", include("apps.rentals.urls")),
    path("raporlar/", include("apps.reports.urls")),
    path("ayarlar/", include("apps.common.urls")),
    path("", dashboard, name="dashboard"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
