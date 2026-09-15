from django.urls import path

from . import views

app_name = "rentals"

urlpatterns = [
    path("", views.rental_list, name="list"),
    path("yeni/", views.rental_create, name="create"),
    path("<int:pk>/", views.rental_detail, name="detail"),
    path("<int:pk>/duzenle/", views.rental_update, name="update"),
    path("<int:pk>/teslim-et/", views.rental_deliver, name="deliver"),
    path("<int:pk>/iade-al/", views.rental_return, name="return"),
    path("<int:pk>/iptal/", views.rental_cancel, name="cancel"),
    path("musteriler/", views.customer_list, name="customer_list"),
    path("musteriler/yeni/", views.customer_create, name="customer_create"),
    path("musteriler/mukerrer-kontrol/", views.customer_duplicate_check, name="customer_duplicate_check"),
    path("musteriler/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("musteriler/<int:pk>/duzenle/", views.customer_update, name="customer_update"),
    path("musteriler/<int:customer_pk>/surucu-ekle/", views.driver_create, name="driver_create"),
    path("musteriler/<int:customer_pk>/surucu-ekle-ajax/", views.driver_quick_create, name="driver_quick_create"),
    path("surucu/<int:pk>/duzenle/", views.driver_update, name="driver_update"),
]
