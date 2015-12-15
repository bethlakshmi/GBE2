from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import costume_changestate
import mock
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    CostumeFactory,
    ProfileFactory
)
from django.core.exceptions import PermissionDenied


class TestCostumeChangestate(TestCase):
    '''Tests for costume_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.costume = CostumeFactory.create()
        self.privileged_user = ProfileFactory.create().user_object
        group, nil = Group.objects.get_or_create(name='Costume Coordinator')
        self.privileged_user.groups.add(group)

    def test_costume_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        request = self.factory.get('costume/changestate/%d' % self.costume.pk)
        request.user = self.privileged_user
        response = costume_changestate(request, self.costume.pk)
        nt.assert_equal(response.status_code, 302)

    @nt.raises(PermissionDenied)
    def test_costume_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        request = self.factory.get('costume/changestate/%d' % self.costume.pk)
        request.user = ProfileFactory.create().user_object
        response = costume_changestate(request, self.costume.pk)
