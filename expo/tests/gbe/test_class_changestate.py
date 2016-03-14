import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import class_changestate
from django.core.exceptions import PermissionDenied
from tests.factories.gbe_factories import (
    ClassFactory,
    ProfileFactory
)
from tests.functions.gbe_functions import grant_privilege


class TestClassChangestate(TestCase):
    '''Tests for act_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.klass = ClassFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def test_class_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        request = self.factory.get('class/changestate/%d' % self.klass.pk)
        request.user = self.privileged_user
        response = class_changestate(request, self.klass.pk)
        nt.assert_equal(response.status_code, 302)

    @nt.raises(PermissionDenied)
    def test_class_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        request = self.factory.get('class/changestate/%d' % self.klass.pk)
        request.user = ProfileFactory().user_object
        response = class_changestate(request, self.klass.pk)
