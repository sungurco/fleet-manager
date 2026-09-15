import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fleet_manager.settings")

app = Celery("fleet_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "gunluk-uyari-kontrolu": {
        "task": "apps.reports.tasks.send_expiry_notifications",
        "schedule": crontab(hour=8, minute=0),  # Her gün sabah 08:00
    },
}
