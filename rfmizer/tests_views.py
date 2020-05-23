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
            self.assertTrue(response.context['lines'])
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
            session.save()
            tab = ManageTable.objects.get(pk=session['tab'])
            self.assertTrue(response.context['lines'])
            self.assertEqual(session['tab_is_new'], False)
            self.assertEqual(tab.name, self.tab_exist.name)
            self.assertEqual(response.redirect_chain,
                             [('/parse/', 302)])

    def test_parse_post(self):
        # with open(self.file) as f:

        file_obj = UserFiles(file=self.file, owner=self.user)
        file_obj.save()
        session = self.client.session
        session['file'] = file_obj.pk
        session['tab'] = self.tab_exist.id
        session.save()
        response = self.client.post('/parse/',
                                    data=self.column_order,
                                    )
        tab = ManageTable.objects.get(pk=session['tab'])
        self.assertEqual(response, [self.tab_exist.slug])


class TestLog(FixturesMixin, TestCase):

    def test_log(self):
        response = self.client.get('/log/')
        self.assertEqual(response.status_code, 200)
