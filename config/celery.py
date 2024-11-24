import multiprocessing
import os
from django.conf import settings

if os.name == 'nt':  # For Windows
    multiprocessing.set_start_method('spawn')

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()