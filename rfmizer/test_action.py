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
        client = Person.objects.get(name='Test')
        client.rfm_move = '333233'
        client.rfm_flag = True
        client.save()
        clients = ActionRocketSMS.get_clients(
            owner=self.user,
            tab=self.tab_exist,
            rfm_move=['333233'],
        )
        self.assertEqual(clients[0], client)


class TestActionRocketSMS(FixturesMixin, TestCase):
    def setUp(self):
        response = self.client.post(self.url,
                                    {'name': 'test_rule_3',
                                     'on_off_rule': False,
                                     'from_to': ['333233', '233133'],
                                     'message': 'test message'},
                                    follow=True)
        rule = Rules.objects.get(name='test_rule_3')
        self.assertEqual(rule.from_to, ['333233', '233133'])

    @mock.patch('rfmizer.action.ActionRocketSMS.sender.check_balance',
                return_value='SMS Принято, статус: SENT')
    def test_run_rules(self, balance_check):

        ActionRocketSMS.run_rules()
        balance_check.assert_called_once()

