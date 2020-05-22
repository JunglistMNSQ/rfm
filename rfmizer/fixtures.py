from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import ManageTable


class FixturesMixin(TestCase):
    def setUp(self):
        super(FixturesMixin, self).setUp()
        self.client = Client()
        self.file = '/Users/vladimir/Documents/testdbsheet.csv'
        self.file_corrupt = '/Users/vladimir/Documents/' \
                            'corrupt_data_testsheet.csv'
        self.user = User(username='TestUser')
        self.user.save()
        self.client.force_login(self.user)
        self.tab_exist = ManageTable(name='test', owner=self.user)
        self.tab_exist.save()
        self.column_order = {'col0': 'date',
                             'col1': 'name',
                             'col2': 'phone',
                             'col3': 'good',
                             'col4': 'pay'}
