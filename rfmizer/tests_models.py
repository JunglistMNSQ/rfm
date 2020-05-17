from django.test import TestCase
from .models import *

# Create your tests here.


class TestProfile(TestCase):

    def setUp(self):
        self.new_user = User(username='u_test')
        self.new_user.save()

    def test_create_user_profile(self):
        self.assertEqual(self.new_user.profile.user, self.new_user)

    def test_notification(self):
        self.new_user.profile.notification('Alert!')
        self.assertEqual(self.new_user.profile.notification_msg,
                         'Alert!')


class TestCsvFileHandler(TestCase):

    def setUp(self):
        self.file = CsvFileHandler('/Users/vladimir/Documents/testdbsheet.csv')

    def test_init(self):
        self.assertTrue(self.file.file)

    def test_get_line(self):
        line = self.file.get_line()
        self.assertEqual(type(line), list)


class TestHandlerRawData(TestCase):

    def setUp(self):
        self.obj = CsvFileHandler('/Users/vladimir/Documents/testdbsheet.csv')
        self.parser = HandlerRawData(self.obj)

    def test_init_with_object(self):
        bound = self.parser.bound_obj
        self.assertEqual(bound, self.obj)

    def test_take_line(self):
        line = self.parser.take_line()
        self.assertEqual(type(line), list)

    def test_take_n_lines(self):
        self.parser.take_lines(n=4)
        self.assertEqual(len(self.parser.raw_data), 4)

    def test_take_all_lines(self):
        self.parser.take_lines()
        self.assertEqual(len(self.parser.raw_data),
                         self.obj.file.line_num)


class TestManageTable(TestCase):

    def setUp(self):
        self.user = User()
        self.user.save()

    def test_save_with_work_slug(self):
        obj1 = ManageTable(name='Test1', owner=self.user)
        obj2 = ManageTable(name='Test1', owner=self.user)
        obj3 = ManageTable(name='Test1', owner=self.user)
        obj1.save()
        obj2.save()
        obj3.save()
        self.assertNotEqual(obj1.slug, obj2.slug)
        self.assertNotEqual(obj3.slug, obj2.slug)
        obj4 = ManageTable(name='T est1', owner=self.user)
        obj5 = ManageTable(name='Tes t1', owner=self.user)
        obj6 = ManageTable(name='Te st *&*^1', owner=self.user)
        obj4.save()
        obj5.save()
        obj6.save()
        self.assertEqual(obj4.slug.find(' '), -1)
        self.assertEqual(obj5.slug.find(' '), -1)
        self.assertEqual(obj6.slug.find(' '), -1)
