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


class TestUploadToParse(UserReadyMixin, TestCase):

    def test_get(self):
        response = self.client.get('/upload/', )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ManageTable.objects.filter(owner=self.user)[0],
                         self.tab_exist)

    def test_create(self):
        with open(self.file) as f:
            response = self.client.post(
                '/upload/',
                {'name': 'test1',
                 'file': f},
                follow=True
            )
            session = self.client.session
            tab = ManageTable.objects.get(pk=session['tab'])
            # self.assertTrue(response.context['lines'])
            self.assertEqual(tab.name, 'test1')
            self.assertTrue(session['tab_is_new'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.redirect_chain,
                             [('/parse/', 302)])

    def test_update(self):
        with open(self.file) as f:
            response = self.client.post(
                '/upload/',
                {'choice_exist_tab': self.tab_exist.id,
                 'file': f},
                follow=True
            )
            session = self.client.session
            tab = ManageTable.objects.get(pk=session['tab'])
            self.assertTrue(response.context['lines'])
            self.assertEqual(session['tab_is_new'], False)
            self.assertEqual(tab.name, self.tab_exist.name)
            self.assertEqual(response.redirect_chain,
                             [('/parse/', 302)])

    # def test_parse_context(self):
    #     response = self.client.post('/parse/', follow=True)
    #     tab = ManageTable.objects.get(pk=self.client.session['tab'])
    #     self.assertEqual(response.redirect_chain, (tab.slug, 302))


class TestLog(UserReadyMixin, TestCase):

    def test_log(self):
        response = self.client.get('/log/')
        self.assertEqual(response.status_code, 200)



