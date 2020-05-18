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

