from django.contrib import messages
from django.shortcuts import redirect, render

from apps.accounts.permissions import role_required

from .forms import SystemSettingsForm
from .models import SystemSettings


@role_required(["ADMIN"])
def settings_view(request):
    settings_obj = SystemSettings.load()
    if request.method == "POST":
        form = SystemSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Ayarlar güncellendi.")
            return redirect("common:settings")
    else:
        form = SystemSettingsForm(instance=settings_obj)
    return render(request, "common/settings_form.html", {"form": form, "title": "Ayarlar"})
