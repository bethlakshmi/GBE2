from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import admin_profile
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import grant_privilege


class TestAdminProfile(TestCase):
    '''Tests for admin_profile  view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Registrar')

    @nt.raises(Http404)
    def test_admin_profile_no_such_profile(self):
        request = self.factory.get('profile/admin/%d' % -1)
        request.user = self.privileged_user
        response = admin_profile(request, -1)

    def test_get(self):
        profile = self.performer.contact
        ProfilePreferencesFactory(profile=profile)
        request = self.factory.get('profile/admin/%d' % profile.pk)
        request.session = {'cms_admin_site': 1}
        request.user = self.privileged_user
        # response = admin_profile(request, profile.pk)
        # nt.assert_true(profile.display_name in response.content)
