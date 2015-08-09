from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import admin_profile
import factories
from django.contrib.auth.models import Group


class TestAdminProfile(TestCase):
    '''Tests for admin_profile  view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        registrar, created = Group.objects.get_or_create(name='Registrar')
        self.privileged_user = factories.ProfileFactory.create().user_object
        self.privileged_user.groups.add(registrar)

    @nt.raises(Http404)
    def test_admin_profile_no_such_profile(self):
        request = self.factory.get('profile/admin/%d' % -1)
        request.user = self.privileged_user
        response = admin_profile(request, -1)
