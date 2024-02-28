import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_MMORPG.settings')

app = Celery('site_MMORPG')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()