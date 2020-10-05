from rfm.celery import celery_app
from .action import ActionRFMizer, ActionRocketSMS


@celery_app.task
def schedule_run_rfmizer():
    return ActionRFMizer.run_rfmizer()


@celery_app.task
def schedule_run_sms_sending():
    return ActionRocketSMS.run_rules()
