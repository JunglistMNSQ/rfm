import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rfm.settings')

celery_app = Celery('rfm')

celery_app.conf.timezone = 'Europe/Minsk'
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'run-rfmizer-at-3-am': {
        'task': 'rfmizer.tasks.schelude_run_rfmizer',
        'schelude': crontab(hour='3', day_of_week='mon-fri')
    },
    'run-sms-sending-at-10-am': {
        'task': 'rfmizer.tasks.schelude_run_sms_sending',
        'schelude': crontab(hour='10', day_of_week='mon-fri')
    },
}
