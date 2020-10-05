from django.test import TestCase
from django.urls import reverse
from unittest import mock
from .fixtures import FixturesMixin
from .models import Person, Tab, User
import hashlib


# Create your tests here.


class TestRegister(FixturesMixin, TestCase):
    def test_create_and_login(self):
        self.client.post('/register/',
                         {'username': 'TestUser1',
                          'email': 'test@test.com',
                          'password': 'password',
                          'password2': 'password'})
        session = self.client.session
        session.save()
        user = User.objects.get_by_natural_key('TestUser1')
        self.assertEqual(user.get_username(), 'TestUser1')
        response = self.client.post('/login/',
                                    {'username': 'TestUser1',
                                     'password': 'password'},
                                    follow=True)
        self.assertEqual(response.redirect_chain, [('/profile/', 302)])

    def test_create_with_different_passwords(self):
        response = self.client.post('/register/',
                                    {'username': 'TestUser1',
                                     'email': 'test@test.com',
                                     'password': 'password1',
                                     'password2': 'password2'})
        self.assertRaisesMessage(response, 'Пароли не совпадают')


class TestLogin(FixturesMixin, TestCase):
    def test_login(self):
        response = self.client.post('/login/',
                                    {'username': 'TestUser',
                                     'password': 'password'},
                                    follow=True)
        self.assertEqual(response.redirect_chain, [('/profile/', 302)])


class TestUploadToParse(FixturesMixin, TestCase):
    def test_get(self):
        response = self.client.get('/upload/', )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tab.objects.filter(owner=self.user)[0],
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
            tab = Tab.objects.get(pk=session['tab'])
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
            self.assertEqual(response.redirect_chain,
                             [('/corrupt_data/',
                               302)])
            self.assertEqual(response.status_code, 200)

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
            tab = Tab.objects.get(pk=session['tab'])
            self.assertTrue(response.context['lines'])
            self.assertEqual(session['tab_is_new'], False)
            self.assertEqual(tab.name, self.tab_exist.name)
            self.assertEqual(response.redirect_chain,
                             [('/parse/', 302)])
            response = self.client.post('/parse/',
                                        self.column_order,
                                        follow=True
                                        )
            tab = Tab.objects.get(pk=session['tab'])
            self.assertEqual(
                response.redirect_chain,
                [('/my_tables/' + tab.slug, 302)]
            )


class TestMyTables(FixturesMixin, TestCase):
    def test_get(self):
        response = self.client.get('/my_tables/')
        qs = response.context['list_tab']
        self.assertSetEqual(
            set(qs),
            {self.tab_exist,
             Tab.objects.get(pk=2),
             Tab.objects.get(pk=3)}
        )
        self.assertEqual(response.status_code, 200)


class TestManageTab(FixturesMixin, TestCase):
    def setUp(self):
        super(TestManageTab, self).setUp()
        self.url = reverse('manage_tab', args=(self.tab_exist.slug, ))

    def test_get_post(self):
        response = self.client.get(self.url)
        session = self.client.session
        session.save()
        self.assertEqual(response.status_code, 200)


class TestDeleteTab(FixturesMixin, TestCase):
    def test_post(self):
        test_tab = Tab(owner=self.user, name='test_tab_del')
        test_tab.save()
        url = reverse('delete', args=(test_tab.slug, ))
        response = self.client.post(url,
                                    follow=True)
        self.assertEqual(response.redirect_chain,
                         [('/my_tables', 302), ('/my_tables/', 301)])


class TestLog(FixturesMixin, TestCase):
    def test_log(self):
        response = self.client.get('/log/')
        self.assertEqual(response.status_code, 200)


class TestClientList(FixturesMixin, TestCase):
    def test_get(self):
        url = reverse('client_list',
                      kwargs={'slug': self.tab_exist.slug, })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestClientCard(FixturesMixin, TestCase):
    def test_get(self):
        new_client = Person.get_new_line(self.data)
        url = reverse('client_card',
                      kwargs={'slug_tab': self.tab_exist.slug,
                              'slug': new_client.slug})
        response = self.client.get(url)
        session = self.client.session
        session.save()
        self.assertEqual(response.status_code, 200)


class TestRulesList(FixturesMixin, TestCase):
    def test_get(self):
        url = reverse('rules', kwargs={'slug': self.tab_exist.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestProfile(FixturesMixin, TestCase):
    def test_get(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    @mock.patch('rfmizer.sms.RocketSMS.check_balance',
                return_value=[True, 25, None])
    def test_post(self, balance_mock):
        password = 'test_sms_pass'
        login = 'test_sms_login'
        response = self.client.post('/profile/',
                                    {'sms_login': login,
                                     'sms_pass': password},
                                    follow=True)
        hash_pass = hashlib.md5(password.encode('utf-8')).hexdigest()
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.profile.sms_login, login)
        self.assertEqual(user.profile.sms_pass, hash_pass)
        self.assertEqual(user.profile.balance, 25)
        self.assertEqual(response.status_code, 200)
        balance_mock.assert_called_once()
