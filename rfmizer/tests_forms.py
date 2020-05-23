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

    def test_parser_form_clean(self):
        form = ParserForm(data=self.column_order)
        res = form.is_valid()
        self.assertTrue(res)
