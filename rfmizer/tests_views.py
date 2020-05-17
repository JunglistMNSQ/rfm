from django.contrib.auth.models import User
from django.test import TestCase, Client
from .views import *

# Create your tests here.


class UserReadyMixin(TestCase):

    def setUp(self):
        super(UserReadyMixin, self).setUp()
        self.client = Client()
        self.user = User(username='TestUser')
        self.user.save()
        self.client.force_login(self.user)
        self.tab_exist = ManageTable(name='SetUpTable', owner=self.user)
        self.tab_exist.save()
        self.file = '/Users/vladimir/Documents/testdbsheet.csv'


class TestRegister(TestCase):

    def setUp(self):
        self.client = Client()

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


class TestUpload(UserReadyMixin, TestCase):

    def test_get(self):
        response = self.client.get('/upload/', )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ManageTable.objects.filter(owner=self.user)[0],
                         self.tab_exist)

    def test_post_create(self):
        with open(self.file) as f:
            response = self.client.post('/upload/',
                                        {'name': 'test1',
                                         'file': f},
                                        follow=True)
            self.assertEqual(response.redirect_chain, [('/parse/', 302)])
            self.assertTrue(ManageTable.objects.get(name='test1'))

    def test_post_update(self):
        with open(self.file) as f:
            response = self.client.post(
                '/upload/',
                {'choice_exist_tab': self.tab_exist,
                 'file': f},
                follow=True
            )
            self.assertEqual(response.redirect_chain, [('/parse/', 302)])


class TestParse(UserReadyMixin, TestCase):

    def test_parse(self):
        response = self.client.get('/parse/')
        self.assertEqual(response.status_code, 200)


class TestLog(UserReadyMixin, TestCase):

    def test_log(self):
        response = self.client.get('/log/')
        self.assertEqual(response.status_code, 200)



