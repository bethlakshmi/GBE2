import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
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
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    def test_register_not_post(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        #TO DO: test details here
