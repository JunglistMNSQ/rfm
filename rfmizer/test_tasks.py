from django.test import TestCase
from .tasks import schelude_run_rfmizer, schelude_run_sms_sending


class TestTasks(TestCase):
    def test_schelude_run_rfmizer(self):
        res = schelude_run_rfmizer()
        self.assertEqual(res, True)

    def test_schelude_run_sms_sending(self):
        res = schelude_run_sms_sending()
        self.assertEqual(res, True)
