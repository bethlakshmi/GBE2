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
from tests.functions.gbe_functions import login_as


class TestUpdateProfile(TestCase):
    '''Tests for update_profile  view'''
    view_name='profile_update'

    def setUp(self):
        self.client = Client()

    def test_update_profile_no_such_profile(self):
        user = UserFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        nt.assert_true(user.profile is not None)
