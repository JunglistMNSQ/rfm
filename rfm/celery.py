import os
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rfm.settings')

celery_app = Celery(
    'rfmzer',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['rfmizer.tasks'],
)

celery_app.conf.timezone = 'django.conf:settings.TIME_ZONE'
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'run-rfmizer-at-3-am': {
        'task': 'rfmizer.tasks.schedule_run_rfmizer',
        'schedule': crontab(hour='3', day_of_week='mon-fri')
    },
    'run-sms-sending-at-10-am': {
        'task': 'rfmizer.tasks.schedule_run_sms_sending',
        'schedule': crontab(hour='10', day_of_week='mon-fri')
    },
}
