import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import update_profile
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import grant_privilege


class TestUpdateProfile(TestCase):
    '''Tests for update_profile  view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    def test_update_profile_no_such_profile(self):
        request = self.factory.get('update_profile/')
        request.session = {'cms_admin_site': 1}
        user = UserFactory()
        request.user = user
        response = update_profile(request)
        nt.assert_true(user.profile is not None)
