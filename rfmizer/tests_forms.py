# from django.contrib.auth.models import User
# from django.test import TestCase, Client
# from .forms import *
# from .models import *
#
#
# class TestCreateOrUpdateForm(TestCase):
#
#     def setUp(self):
#         self.user = User(username='TestUser')
#         self.user.save()
#         self.table = ManageTable(name_table='test',
#                                  owner=self.user)
#         self.table.save()
#
#     def test_init_form(self):
#         form = CreateOrUpdateTable(owner=self.user)
#         self.assertTrue(form)
#
#     def test_upload_init(self):
#         form = CreateOrUpdateTable(owner=self.user)
#         form.file = '/Users/vladimir/Documents/testdbsheet.csv'
#         self.assertTrue(form['choice_exist_tab'][1])
#
#     def test_upload_post_create(self):
#         form = CreateOrUpdateTable(owner=self.user)
#         form.file = '/Users/vladimir/Documents/testdbsheet.csv'
#         form.cleaned_data['name_table'] = 'test1'
#         tab = form.save(commit=False)
#         print(tab.name_table)
#         tab.owner = self.user
#         tab.save()
#         print(tab.owner)
#         self.assertTrue(tab.on_off)

