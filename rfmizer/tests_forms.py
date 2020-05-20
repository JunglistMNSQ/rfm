from django.contrib.auth.models import User
from django.test import TestCase, Client
from .forms import *
from .models import *


class TestCreateOrUpdateForm(TestCase):

    def setUp(self):
        self.user = User(username='TestUser')
        self.user.save()
        self.table = ManageTable(name='test',
                                 owner=self.user)
        self.table.save()

    def test_init_form(self):
        form = CreateOrUpdateTable(owner=self.user)
        self.assertTrue(form)

    def test_upload_init(self):
        form = CreateOrUpdateTable(owner=self.user)
        form.file = '/Users/vladimir/Documents/testdbsheet.csv'
        file = UserFiles(file=form.file, owner=self.user)
        file.save()
        self.assertTrue(file.file)
        self.assertTrue(form['choice_exist_tab'][1])

    def test_upload_post_create(self):
        form = CreateOrUpdateTable(owner=self.user)
        form.file = '/Users/vladimir/Documents/testdbsheet.csv'
        form.name = 'test1'
        tab = form.save(commit=False)
        tab.owner = self.user
        tab.save()
        file = UserFiles(file=form.file, owner=self.user)
        file.save()
        self.assertTrue(file.file)
        self.assertTrue(tab.on_off)


class TestParserForm(TestCase):
    def setUp(self):
        self.user = User()
        self.user.save()
        self.tab = ManageTable(name='test', owner=self.user)
        self.tab.save()
        file = CsvFileHandler('/Users/vladimir/Documents/testdbsheet.csv')
        self.parser = HandlerRawData(file)
        self.parser.owner = self.user

    def test_parser_form_init(self):
        form = ParserForm(parser=self.parser)
        self.assertEqual(form.parser, self.parser)

    def test_parser_form_clean(self):
        form_data = {'col0': 'name',
                     'col1': 'phone',
                     'col2': 'date',
                     'col3': 'pay',
                     'col4': 'good'}
        form = ParserForm(parser=self.parser, data=form_data)
        form.is_valid()
        cd = form.cleaned_data

        self.assertEqual(cd['col0'], self.parser.col0)
        self.assertEqual(cd['col1'], self.parser.col1)
        self.assertEqual(cd['col2'], self.parser.col2)
        self.assertEqual(cd['col3'], self.parser.col3)
        self.assertEqual(cd['col4'], self.parser.col4)
        self.assertEqual(self.parser.owner, self.user)
        self.assertEqual(self.parser.tab, self.tab)

