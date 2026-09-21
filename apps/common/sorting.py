"""
Tüm liste sayfalarında ortak kullanılan, backend (ORM) taraflı sütun
sıralama yardımcıları. Yeni bir liste sayfası eklerken JS ile client-side
sıralama YAZMAYIN — bu modülü ve templates/partials/sortable_th.html
bileşenini (bkz. {% load sortable %} / {% sortable_th %}) kullanın.
"""

ALLOWED_DIRECTIONS = {"asc", "desc"}


def _read_sort_params(request):
    direction = request.GET.get("direction", "asc")
    if direction not in ALLOWED_DIRECTIONS:
        direction = "asc"
    return request.GET.get("sort", ""), direction


def apply_sort(request, queryset, field_map):
    """
    field_map: {url_sort_anahtari: orm_alan_yolu (str veya str listesi)}
    Örn: {"musteri": "customer__full_name", "tutar": "total_price"}

    Geçersiz/boş ?sort= parametresinde queryset'in mevcut sırası
    (genelde modelin Meta.ordering'i) korunur, hiçbir şey değişmez.
    """
    sort_key, direction = _read_sort_params(request)
    orm_fields = field_map.get(sort_key)
    if not orm_fields:
        return queryset, {"current_sort": "", "current_direction": "asc"}

    if isinstance(orm_fields, str):
        orm_fields = [orm_fields]
    ordering = [f"-{f}" if direction == "desc" else f for f in orm_fields]
    return queryset.order_by(*ordering), {"current_sort": sort_key, "current_direction": direction}


def apply_sort_to_list(request, rows, key_map):
    """
    Queryset'e dönüştürülemeyen, Python tarafında hesaplanmış satır
    listeleri (örn. rapor tabloları) için apply_sort ile aynı
    ?sort=&direction= sözleşmesini uygulayan karşılığı.

    key_map: {url_sort_anahtari: lambda row: <karşılaştırılabilir değer>}
    """
    sort_key, direction = _read_sort_params(request)
    key_func = key_map.get(sort_key)
    if not key_func:
        return rows, {"current_sort": "", "current_direction": "asc"}

    sorted_rows = sorted(rows, key=key_func, reverse=(direction == "desc"))
    return sorted_rows, {"current_sort": sort_key, "current_direction": direction}
