from django.test import TestCase
from datetime import date
from .models import CsvFileHandler, HandlerRawData, Person, \
    PhoneNumberField, Tab, UserFiles
from .fixtures import FixturesMixin

# Create your tests here.


class TestProfile(FixturesMixin, TestCase):
    def test_create_user_profile(self):
        self.assertEqual(self.user.profile.user, self.user)

    def test_notification(self):
        self.user.profile.notification('Alert!')
        self.assertEqual(self.user.profile.notification_msg,
                         'Alert!')


class TestCsvFileHandler(FixturesMixin, TestCase):

    def setUp(self):
        super(TestCsvFileHandler, self).setUp()
        self.obj = CsvFileHandler(self.file)

    def test_init(self):
        self.assertTrue(self.obj.file)

    def test_get_line(self):
        line = self.obj.get_line()
        self.assertEqual(type(line), list)

    def test_bom_replace(self):
        line = ['\ufeffData', 'data2', 'dada']
        line = self.obj.bom_replace(line)
        self.assertEqual(line[0], 'Data')


class TestHandlerRawData(FixturesMixin, TestCase):
    def setUp(self):
        super(TestHandlerRawData, self).setUp()
        self.obj = CsvFileHandler(self.file)
        self.parser = HandlerRawData(self.obj)
        self.parser.order = self.order

    def test_init_with_object(self):
        bound = self.parser.bound_obj
        self.assertEqual(bound, self.obj)

    def test_take_line(self):
        line = self.parser.take_line()
        self.assertEqual(type(line), list)

    def test_take_n_lines(self):
        self.parser.take_lines(n=2)
        self.assertEqual(len(self.parser.raw_data), 2)

    def test_take_all_lines(self):
        self.parser.take_lines()
        self.assertEqual(len(self.parser.raw_data),
                         self.obj.file.line_num)

    def test_parse(self):
        self.parser.owner = self.user
        self.parser.tab = self.tab_exist
        result = self.parser.parse()
        self.assertEqual(result, False)

    def test_get_or_create_person(self):
        name_list = ['Евгения', 'Анжела  Олеговна', 'Елена', 'Test']
        self.parser.owner = self.user
        self.parser.tab = self.tab_exist
        self.parser.parse()
        person_list = Person.objects.filter(
            tab=self.tab_exist
        )
        self.assertTrue(person_list)
        self.assertEqual(self.parser.not_condition_data, [])
        for person in person_list:
            self.assertTrue(str(person) in name_list)

    def test_corrupt_data_parse(self):
        obj = CsvFileHandler(self.file_bad)
        parser = HandlerRawData(obj)
        parser.owner = self.user
        parser.tab = self.tab_exist
        for key, value in self.column_order.items():
            setattr(parser, key, value)
        parser.parse()
        self.assertTrue(parser.not_condition_data)


class TestPerson(FixturesMixin, TestCase):
    def setUp(self):
        super(TestPerson, self).setUp()
        self.prep_line = {'owner': self.user,
                          'tab': self.tab_exist,
                          'name': 'Екатерина великая',
                          'phone': '+375291516065',
                          'date': '23.04.2020',
                          'pay': '135',
                          'good': 'Печенеги'}

    def test_create_person(self):
        Person.get_new_line(self.prep_line)
        person = Person.objects.get(phone=self.prep_line['phone'])
        self.assertEqual(person.name, self.prep_line['name'].title())

    def test_clean_data(self):
        Person.get_new_line(self.prep_line)
        person = Person.objects.get(phone=self.prep_line['phone'])
        self.assertIsInstance(person.phone, PhoneNumberField.attr_class)
        self.assertIsInstance(person.last_deal, date)

    def test_add_deal(self):
        deals = [
            {'date': '20-05-2020',
             'pay': '140',
             'good': 'капуста'.title()},
            {'date': '20-03-2020',
             'pay': '50',
             'good': 'Морковка'.title()},
            {'date': '20-05-2020',
             'pay': '90',
             'good': 'Кабачок'.title()},
            {'date': '20-05-2020',
             'pay': '90',
             'good': 'Кабачок'.title()}
        ]
        Person.get_new_line(self.prep_line)
        person = Person.objects.get(phone=self.prep_line['phone'])
        for deal in deals:
            person.add_deal(deal)
        self.assertEqual(person.deal_count, 4)
        self.assertEqual(person.pays, 415)
        self.assertEqual(str(person.last_deal), '2020-05-20')


class TestUserFiles(FixturesMixin, TestCase):
    def test_save_file(self):
        new_file = UserFiles()
        new_file.file = self.file
        new_file.owner = self.user
        new_file.save()
        self.assertTrue(UserFiles.object.get())


class TestManageTable(FixturesMixin, TestCase):
    def setUp(self):
        super(TestManageTable, self).setUp()
        self.clients = [
            {'name': 'test1',
             'phone': '+375296666665',
             'date': '02.06.2018',
             'good': 'testt',
             'pay': 60,
             'owner': self.user,
             'tab': self.tab_exist},
            {'name': 'test2',
             'phone': '+375291666666',
             'date': '02.06.2016',
             'good': 'ttestt',
             'pay': 40,
             'owner': self.user,
             'tab': self.tab_exist}
        ]
        for client in self.clients:
            Person.get_new_line(client)

    def test_save_with_work_slug(self):
        obj1 = Tab(name='Test1', owner=self.user)
        obj2 = Tab(name='Test1', owner=self.user)
        obj3 = Tab(name='Test1', owner=self.user)
        obj1.save()
        obj2.save()
        obj3.save()
        self.assertNotEqual(obj1.slug, obj2.slug)
        self.assertNotEqual(obj3.slug, obj2.slug)
        obj4 = Tab(name='T est1', owner=self.user)
        obj5 = Tab(name='Tes t1', owner=self.user)
        obj6 = Tab(name='Te st *&*^1', owner=self.user)
        obj4.save()
        obj5.save()
        obj6.save()
        self.assertEqual(obj4.slug.find(' '), -1)
        self.assertEqual(obj5.slug.find(' '), -1)
        self.assertEqual(obj6.slug.find(' '), -1)

    def test_rfmizer(self):
        res = self.tab_exist.rfmizer()
        self.assertEqual(res, 'Установите настройки RFM.')
        for key, value in self.rfm.items():
            setattr(self.tab_exist, key, value)
        self.tab_exist.save()
        self.tab_exist.recency_calc()
        res = self.tab_exist.rfmizer()
        self.assertEqual(res, 'RFM успешно пересчитан.')
        clients = Person.objects.filter(tab=self.tab_exist)
        for client in clients:
            self.assertNotEqual(client.rfm_category, '000')
            self.assertNotEqual(client.rfm_move, '000000')

    def test_recency_calc(self):
        data = self.rfm
        tab = self.tab_exist
        for key, value in data.items():
            setattr(tab, key, value)
        tab.save()
        tab.recency_calc()
        self.assertTrue(tab.recency_1,)
        self.assertTrue(tab.recency_2,)
