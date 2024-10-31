import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'midterm.settings')
app = Celery('midterm', broker='amqp://guest:guest@rabbitmq:5672//')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()