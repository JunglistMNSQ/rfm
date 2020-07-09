from django.test import TestCase
from .action import *
from .fixtures import FixturesMixin
from unittest import mock


class TestActionsRFMizer(FixturesMixin, TestCase):
    def test_get_active_users(self):
        list_of_users = ActionRFMizer.get_active_users()
        self.assertEqual(len(list_of_users), 2)

    def test_get_active_tab(self):
        tabs_are_active = ActionRFMizer.get_active_tabs()
        self.assertEqual(len(tabs_are_active), 2)

    def test_run_rfmizer(self):
        clients = Person.objects.filter(
            tab=ManageTable.objects.get(pk=2)
        )
        for client in clients:
            self.assertEqual(client.rfm_category, '000')
        ActionRFMizer.run_rfmizer()
        clients = Person.objects.filter(
            tab=ManageTable.objects.get(pk=2)
        )
        for client in clients:
            self.assertNotEqual(client.rfm_category, '000')

    def test_get_rules(self):
        rules = ActionRocketSMS.get_rules()
        self.assertIsNotNone(rules)

    def test_get_clients(self):
        clients = ActionRocketSMS.get_clients(
            owner=self.user,
            tab=self.tab_exist,
            rfm_move=['333233'],
        )
        self.assertIsNotNone(clients[0])


class TestActionRocketSMS(FixturesMixin, TestCase):
    @mock.patch('rfmizer.action.ActionRocketSMS.sender.check_balance',
                return_value='SMS Принято, статус: SENT')
    def test_run_rules(self, balance_check):

        ActionRocketSMS.run_rules()
        balance_check.assert_called_once()

