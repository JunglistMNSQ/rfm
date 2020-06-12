from django.contrib.auth.models import User
from django.test import TestCase, Client
from .models import *


class FixturesMixin(TestCase):
    def setUp(self):
        super(FixturesMixin, self).setUp()
        self.client = Client()
        self.file = '/Users/vladimir/Documents/testdbsheet.csv'
        self.file_corrupt = '/Users/vladimir/Documents/' \
                            'corrupt_data_testsheet.csv'
        self.user = User(username='TestUser', password='password')
        self.user.save()
        self.user_1 = User(username='TestUser_1', password='password')
        self.user_1.save()
        self.user_2 = User(username='TestUser_2', password='password')
        self.user_2.is_active = False
        self.user_2.save()
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
                    'recency_raw_1': 10,
                    'recency_raw_2': 5,
                    'frequency_1': 3,
                    'frequency_2': 5,
                    'monetary_1': 100,
                    'monetary_2': 200,
                    'on_off': True}
        self.order = ['date', 'name', 'phone', 'good', 'pay']
        self.tab_exist_1 = ManageTable(name='test_test',
                                       owner=self.user)
        for key, value in self.rfm.items():
            setattr(self.tab_exist_1, key, value)
        self.tab_exist_1.recency_calc()
        self.tab_exist_1.save()
        self.f = CsvFileHandler(self.file)
        self.p = HandlerRawData(self.f)
        self.p.order = self.order
        self.p.owner = self.user
        self.p.tab = self.tab_exist_1
        self.p.parse()
