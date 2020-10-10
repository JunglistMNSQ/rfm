from celery import shared_task
from .action import ActionRFMizer, ActionRocketSMS


@shared_task
def schedule_run_rfmizer():
    return ActionRFMizer.run_rfmizer()


@shared_task
def schedule_run_sms_sending():
    return ActionRocketSMS.run_rules()
