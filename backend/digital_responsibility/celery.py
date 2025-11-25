import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "digital_responsibility.settings")

app = Celery("digital_responsibility")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
