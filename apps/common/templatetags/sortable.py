from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def sortable_th(context, label, field):
    """
    Sıralanabilir tablo başlığı standardı — bkz. static/css/theme.css
    başındaki "SIRALANABİLİR TABLO STANDARDI" notu.

    Kullanım: {% sortable_th "Müşteri No" "musteri_no" %}

    "field" değeri, view'in apps.common.sorting.apply_sort(...) /
    apply_sort_to_list(...) çağrısına verdiği field_map/key_map
    sözlüğündeki anahtarla birebir eşleşmelidir. Bu çağrılar context'e
    current_sort / current_direction anahtarlarını zaten ekler.

    Not: inclusion_tag yerine simple_tag + render_to_string kullanılıyor —
    inclusion_tag'in dayandığı Context.new()/__copy__ mekanizması bu
    projenin Python sürümüyle (3.14) uyumsuz (Django 5.0.6'nın
    context.py içindeki copy(super()) numarası AttributeError veriyor).
    """
    request = context["request"]
    current_sort = context.get("current_sort", "")
    current_direction = context.get("current_direction", "asc")

    is_active = bool(field) and current_sort == field
    next_direction = "desc" if (is_active and current_direction == "asc") else "asc"

    params = request.GET.copy()
    params["sort"] = field
    params["direction"] = next_direction

    html = render_to_string("partials/sortable_th.html", {
        "label": label,
        "url": f"?{params.urlencode()}",
        "is_active": is_active,
        "direction": current_direction if is_active else "",
    })
    return mark_safe(html)
