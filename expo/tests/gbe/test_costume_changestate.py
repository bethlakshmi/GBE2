import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import costume_changestate
from tests.factories.gbe_factories import (
    CostumeFactory,
    ProfileFactory
)
from django.core.exceptions import PermissionDenied
from tests.functions.gbe_functions import grant_privilege


class TestCostumeChangestate(TestCase):
    '''Tests for costume_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.costume = CostumeFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Costume Coordinator')

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
        request.user = ProfileFactory().user_object
        response = costume_changestate(request, self.costume.pk)
