from django.test import TestCase
from .fixtures import FixturesMixin
from .views import *

# Create your tests here.


class TestRegister(FixturesMixin, TestCase):
    def test_register_response(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_create_user(self):
        response = self.client.post('/register/',
                                    {'username': 'TestUser',
                                     'email': 'test@test.com',
                                     'password': 'password',
                                     'password2': 'password'})
        user = User.objects.get_by_natural_key('TestUser')
        self.assertEqual(user.get_username(), 'TestUser')


class TestUploadToParse(FixturesMixin, TestCase):
    def test_get(self):
        response = self.client.get('/upload/', )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ManageTable.objects.filter(owner=self.user)[0],
                         self.tab_exist)

    def test_create_and_parse_corrupt_file(self):
        with open(self.file) as f:
            response = self.client.post(
                '/upload/',
                {'name': 'test1',
                 'file': f},
                follow=True
            )
            session = self.client.session
            session.save()
            tab = ManageTable.objects.get(pk=session['tab'])
            self.assertTrue(response.context['lines'])
            self.assertEqual(tab.name, 'test1')
            self.assertTrue(session['tab_is_new'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.redirect_chain,
                             [('/parse/', 302)])

            response = self.client.post('/parse/',
                                        {'col4': 'date',
                                         'col3': 'name',
                                         'col2': 'phone',
                                         'col1': 'good',
                                         'col0': 'pay'},
                                        follow=True
                                        )
            # self.assertEqual(response.redirect_chain, [('corrupt', 302)])

    def test_update_and_parse(self):
        with open(self.file) as f:
            response = self.client.post(
                '/upload/',
                {'choice_exist_tab': self.tab_exist.id,
                 'file': f},
                follow=True
            )
            session = self.client.session
            session.save()
            tab = ManageTable.objects.get(pk=session['tab'])
            self.assertTrue(response.context['lines'])
            self.assertEqual(session['tab_is_new'], False)
            self.assertEqual(tab.name, self.tab_exist.name)
            self.assertEqual(response.redirect_chain,
                             [('/parse/', 302)])
            response = self.client.post('/parse/',
                                        self.column_order,
                                        follow=True
                                        )
            tab = ManageTable.objects.get(pk=session['tab'])
            self.assertEqual(
                response.redirect_chain,
                [('/my_tables/' + self.tab_exist.slug, 302)]
            )


class TestMyTables(FixturesMixin, TestCase):
    def test_get(self):
        response = self.client.get('/my_tables/')
        tabs_on_page = response.context['list_tab']
        tabs_in_db = ManageTable.objects.filter(owner=self.user)
        self.assertQuerysetEqual(tabs_on_page, ['<ManageTable: test>'])
        self.assertEqual(response.status_code, 200)


class TestDeleteTab(FixturesMixin, TestCase):
    def test_post(self):
        test_tab = ManageTable(owner=self.user, name='test_del')
        test_tab.save()
        self.assertEqual(test_tab.name, 'test_del')
        response = self.client.post('/delete/')
        self.assertFalse(test_tab)

class TestLog(FixturesMixin, TestCase):
    def test_log(self):
        response = self.client.get('/log/')
        self.assertEqual(response.status_code, 200)
