from django.test import TestCase
from unittest import mock
from .action import ActionRFMizer, ActionRocketSMS
from .fixtures import FixturesMixin
from .models import ActionLog, Person, Tab


class TestActionsRFMizer(FixturesMixin, TestCase):
    def test_get_active_users(self):
        list_of_users = ActionRFMizer.get_active_users()
        self.assertEqual(len(list_of_users), 2)

    def test_get_active_tab(self):
        tabs_are_active = ActionRFMizer.get_active_tabs()
        self.assertEqual(len(tabs_are_active), 2)

    def test_run_rfmizer(self):
        clients = Person.objects.filter(
            tab=Tab.objects.get(pk=2)
        )
        for client in clients:
            self.assertEqual(client.rfm_category, '000')
        ActionRFMizer.run_rfmizer()
        clients = Person.objects.filter(
            tab=Tab.objects.get(pk=2)
        )
        for client in clients:
            self.assertNotEqual(client.rfm_category, '000')

    def test_get_rules(self):
        rules = ActionRocketSMS.get_rules()
        self.assertIsNotNone(rules)


class TestActionRocketSMS(FixturesMixin, TestCase):
    @mock.patch('rfmizer.action.ActionRocketSMS.sender.check_balance',
                return_value=(True, 25, None))
    @mock.patch('rfmizer.action.ActionRocketSMS.sender.send_sms',
                return_value='SMS Принято, статус: SENT')
    def test_run_rules(self, balance_check, send_sms):
        ActionRocketSMS.run_rules()
        balance_check.assert_called_once()
        send_sms.assert_called_once()
        self.assertTrue(ActionLog.objects.all())

    @mock.patch('rfmizer.action.ActionRocketSMS.sender.check_balance',
                return_value=(False, 0, 'Не достаточно кредитов '
                                        'для отправки смс - 0'))
    def test_run_rules_with_zero_balance(self, balance_check):
        ActionRocketSMS.run_rules()
        balance_check.assert_called_once()
        self.assertEqual(
            str(ActionLog.objects.all()[0]),
            'Не достаточно кредитов для отправки смс - 0'
        )
