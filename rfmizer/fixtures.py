from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from .models import CsvFileHandler, HandlerRawData, Tab


class FixturesMixin(TestCase):
    fixtures = ['fixtures.json']

    def setUp(self):
        self.client = Client()
        self.file = './rfmizer/fixtures/testdbsheet.csv'
        self.file_bad = './rfmizer/fixtures/corrupt_data_testsheet.csv'
        self.user = User.objects.get(pk=1)
        self.tab_exist = Tab.objects.get(pk=1)
        self.client.force_login(self.user)
        self.data = {'name': 'test',
                     'phone': '+375291212121',
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
        self.f = CsvFileHandler(self.file)
        self.handler = HandlerRawData(self.f)
        self.handler.order = self.order
        self.handler.owner = self.user
        self.handler.tab = Tab.objects.get(pk=2)
        self.handler.parse()
        self.url = reverse(
            'new_rule', kwargs={'slug': self.tab_exist.slug}
        )
