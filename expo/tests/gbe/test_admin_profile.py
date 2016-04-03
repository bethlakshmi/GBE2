from django.shortcuts import get_object_or_404
from django.http import Http404
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.models import Profile


class TestAdminProfile(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'admin_profile'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    def test_admin_profile_no_such_profile(self):
        no_such_id = Profile.objects.latest('pk').pk + 1
        url = reverse(self.view_name,
                      args=[no_such_id],
                      urlconf="gbe.urls")
        login_as(self.privileged_user,self)
        response = self.client.get(url)
        nt.assert_equal(404, response.status_code)

    # def test_get(self):
    #     profile = self.performer.contact
    #     ProfilePreferencesFactory(profile=profile)

    #     url = reverse(self.view_name,
    #                   args=[profile.pk],
    #                   urlconf="gbe.urls")
    #     login_as(self.privileged_user,self)
    #     response = self.client.get(url)

    #     nt.assert_equal(200, response.status_code)
