from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import ManageTable, Rules


class FixturesMixin(TestCase):
    def setUp(self):
        super(FixturesMixin, self).setUp()
        self.client = Client()
        self.file = '/Users/vladimir/Documents/testdbsheet.csv'
        self.file_corrupt = '/Users/vladimir/Documents/' \
                            'corrupt_data_testsheet.csv'
        self.user = User(username='TestUser', password='password')
        self.user.save()
        self.client.force_login(self.user)
        self.tab_exist = ManageTable(name='test',
                                     owner=self.user)
        self.tab_exist.save()
        self.data = {'name': 'test',
                     'phone': '+375291516065',
                     'date': '02.06.2019',
                     'good': 'test',
                     'pay': 42,
                     'owner': self.user,
                     'tab': self.tab_exist}
        self.column_order = {'col0': 'date',
                             'col1': 'name',
                             'col2': 'phone',
                             'col3': 'good',
                             'col4': 'pay'}
        self.rule = Rules(tab=self.tab_exist,
                          owner=self.user,
                          name='test_rule',
                          from_to='333233',
                          message='test message')
        self.rule.save()
        self.rfm = {'choice_rec_1': 1,
                    'choice_rec_2': 1,
                    'recency_raw_1': 5,
                    'recency_raw_2': 10,
                    'frequency_1': 5,
                    'frequency_2': 3,
                    'monetary_1': 200,
                    'monetary_2': 100}
