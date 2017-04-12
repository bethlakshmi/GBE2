import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestRegister(TestCase):
    '''Tests for register  view'''
    view_name = 'register'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')
        self.counter = 0

    def get_post_data(self):
        self.counter += 1
        email = "new%d@last.com" % self.counter
        data = {'username': 'test%d' % self.counter,
                'first_name': 'new first',
                'last_name': 'new last',
                'email': email,
                'password1': 'test',
                'password2': 'test'}
        return data

    def test_register_get(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        response = self.client.get(url, follow=True)
        assert("Create an Account" in response.content)

    def test_register_post(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertRedirects(
            response,
            reverse('profile_update', urlconf='gbe.urls'))

    def test_register_redirect(self):
        url = "%s?next=%s" % (
            reverse(self.view_name, urlconf='gbe.urls'),
            reverse('volunteer_create', urlconf='gbe.urls'))

        response = self.client.post(url, self.get_post_data(), follow=True)
        self.assertRedirects(response, "%s?next=%s" % (
            reverse('profile_update', urlconf='gbe.urls'),
            reverse('volunteer_create', urlconf='gbe.urls')))

    def test_register_post_nothing(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        response = self.client.post(url, {'data': 'bad'}, follow=True)
        self.assertIn("This field is required.", response.content)
