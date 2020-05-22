from .fixtures import FixturesMixin
from django.test import TestCase
from .forms import *
from .models import *


class TestCreateOrUpdateForm(FixturesMixin, TestCase):
    def test_init_form(self):
        form = CreateOrUpdateTable(owner=self.user)
        self.assertTrue(form)

    def test_upload_init(self):
        form = CreateOrUpdateTable(owner=self.user)
        form.file = self.file
        file = UserFiles(file=form.file, owner=self.user)
        file.save()
        self.assertTrue(file.file)
        self.assertTrue(form['choice_exist_tab'][1])

    def test_upload_post_create(self):
        form = CreateOrUpdateTable(owner=self.user)
        form.file = self.file
        form.name = 'test1'
        tab = form.save(commit=False)
        tab.owner = self.user
        tab.save()
        file = UserFiles(file=form.file, owner=self.user)
        file.save()
        self.assertTrue(file.file)
        self.assertTrue(tab.on_off)


class TestParserForm(FixturesMixin, TestCase):
    def setUp(self):
        super(TestParserForm, self).setUp()
        self.reader = CsvFileHandler(self.file)
        self.parser = HandlerRawData(self.reader)
        self.parser.owner = self.user

    def test_parser_form_init(self):
        form = ParserForm(parser=self.parser)
        self.assertEqual(form.parser, self.parser)

    def test_parser_form_clean(self):
        form = ParserForm(parser=self.parser, data=self.column_order)
        form.is_valid()
        cd = form.cleaned_data
        self.assertEqual(cd['col0'], self.parser.col0)
        self.assertEqual(cd['col1'], self.parser.col1)
        self.assertEqual(cd['col2'], self.parser.col2)
        self.assertEqual(cd['col3'], self.parser.col3)
        self.assertEqual(cd['col4'], self.parser.col4)
        self.assertEqual(self.parser.owner, self.user)
