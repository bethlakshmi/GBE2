from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import update_profile
from django.contrib.auth.models import Group
from tests.factories import gbe_factories as factories


class TestUpdateProfile(TestCase):
    '''Tests for update_profile  view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        registrar, created = Group.objects.get_or_create(name='Registrar')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(registrar)

    def test_update_profile_no_such_profile(self):
        request = self.factory.get('update_profile/')
        request.session = {'cms_admin_site': 1}
        user = factories.UserFactory.create()
        request.user = user
        response = update_profile(request)
        nt.assert_true(user.profile is not None)
