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
        self.assertQuerysetEqual(tabs_on_page, ['<ManageTable: test>'])
        self.assertEqual(response.status_code, 200)


class TestDeleteTab(FixturesMixin, TestCase):
    def test_post(self):
        test_tab = ManageTable(owner=self.user, name='test_tab_del')
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
    def test_get_post(self):
        new_client = Person.get_new_line(self.data)
        url = reverse('client_card',
                      kwargs={'slug_tab': self.tab_exist.slug,
                              'slug': new_client.slug})
        response = self.client.get(url)
        session = self.client.session
        session.save()
        self.assertEqual(response.status_code, 200)
        # response = self.client.post(url,
        #                             {'active_client': False,
        #                              'phone': new_client.phone.as_e164})
        # self.assertEqual(new_client.active_client, False)


class TestRulesList(FixturesMixin, TestCase):
    def test_get(self):
        url = reverse('rules', kwargs={'slug': self.tab_exist.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestNewRule(FixturesMixin, TestCase):
    def test_get(self):
        url = reverse('new_rule', kwargs={'slug': self.tab_exist.slug})
        response = self.client.get(url)
        session = self.client.session
        session.save()
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url,
                                   {'name': 'test_rule',
                                    'on_off_rule': True,
                                    'from_to': ['333233', '233133'],
                                    'message': 'test message'},
                                   follow=True)
        rule = Rules.objects.get(name='test_rule')
        self.assertEqual(response.redirect_chain, [302, rule.slug])


class TestEditRule(FixturesMixin, TestCase):
    def test_create_rule(self):
        url = reverse('rule', kwargs={'slug_tab': self.tab_exist.slug,
                                      'slug': self.rule.slug})
        response = self.client.get(url)
        session = self.client.session
        session.save()
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url,
                                    {'on_off_rule': False})
        # self.assertEqual(self.rule.on_off_rule, False)
