from django.test import TestCase
from .action import *
from .fixtures import FixturesMixin


class TestActionsRFMizer(FixturesMixin, TestCase):
    def test_get_active_users(self):
        list_of_users = ActionRFMizer.get_active_users()
        self.assertEqual(len(list_of_users), 2)

    def test_get_active_tab(self):
        tabs_are_active = ActionRFMizer.get_active_tabs()
        self.assertEqual(len(tabs_are_active), 2)

    def test_run_rfmizer(self):
        clients = Person.objects.all()
        for client in clients:
            self.assertEqual(client.rfm_category, '000')
        res = ActionRFMizer.run_rfmizer()
        clients = Person.objects.all()
        for client in clients:
            self.assertNotEqual(client.rfm_category, '000')


class TestActionSMSSender(FixturesMixin, TestCase):
    def test_get_rules(self):
        rules = ActionSMSSender.get_rules()
        self.assertEqual(len(rules), 1)

    # def test_run_rules(self):
    #     clients



