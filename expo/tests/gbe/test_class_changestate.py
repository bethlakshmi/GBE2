import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from tests.factories.gbe_factories import (
    ClassFactory,
    ProfileFactory
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestClassChangestate(TestCase):
    '''Tests for act_changestate view'''
    view_name = 'class_changestate'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.klass = ClassFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def test_class_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.klass.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)


    def test_class_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        url = reverse(self.view_name,
                      args=[self.klass.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)
