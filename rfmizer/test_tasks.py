from django.test import TestCase
from .tasks import schedule_run_rfmizer, schedule_run_sms_sending


class TestTasks(TestCase):
    def test_schedule_run_rfmizer(self):
        res = schedule_run_rfmizer()
        self.assertEqual(res, True)

    def test_schedule_run_sms_sending(self):
        res = schedule_run_sms_sending()
        self.assertEqual(res, True)
