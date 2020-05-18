from django.test import TestCase
from .models import *

# Create your tests here.


class SetUpMixin(TestCase):
    def setUp(self):
        super(SetUpMixin, self).setUp()
        self.file = '/Users/vladimir/Documents/testdbsheet.csv'
        self.user = User()
        self.user.save()


class TestProfile(TestCase):

    def setUp(self):
        super(TestProfile, self).setUp()
        self.new_user = User(username='u_test')
        self.new_user.save()

    def test_create_user_profile(self):
        self.assertEqual(self.new_user.profile.user, self.new_user)

    def test_notification(self):
        self.new_user.profile.notification('Alert!')
        self.assertEqual(self.new_user.profile.notification_msg,
                         'Alert!')


class TestCsvFileHandler(SetUpMixin, TestCase):

    def setUp(self):
        super(TestCsvFileHandler, self).setUp()
        self.obj = CsvFileHandler(self.file)

    def test_init(self):
        self.assertTrue(self.obj.file)

    def test_get_line(self):
        line = self.obj.get_line()
        self.assertEqual(type(line), list)


class TestHandlerRawData(SetUpMixin, TestCase):

    def setUp(self):
        super(TestHandlerRawData, self).setUp()
        self.obj = CsvFileHandler(self.file)
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


class TestUserFiles(SetUpMixin, TestCase):

    def test_save_file(self):
        new_file = UserFiles()
        new_file.file = self.file
        new_file.owner = self.user
        new_file.save()
        self.assertTrue(UserFiles.object.get())



    pass




class TestManageTable(SetUpMixin, TestCase):
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
