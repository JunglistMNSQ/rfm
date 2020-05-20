from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import ManageTable


class FixturesMixin(TestCase):
    def setUp(self):
        super(FixturesMixin, self).setUp()
        self.client = Client()
        self.file = '/Users/vladimir/Documents/testdbsheet.csv'
        self.user = User()
        self.user.save()
        self.client.force_login(self.user)
        self.tab_exist = ManageTable(name='test', owner=self.user)
        self.tab_exist.save()
        self.parse_form_data = {'col0': 'name',
                                'col1': 'phone',
                                'col2': 'date',
                                'col3': 'pay',
                                'col4': 'good'}
