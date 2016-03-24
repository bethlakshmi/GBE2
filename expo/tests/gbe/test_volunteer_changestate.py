import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import volunteer_changestate
from tests.factories.gbe_factories import (
    VolunteerFactory,
    ProfileFactory
)
from tests.functions.gbe_functions import grant_privilege
from django.core.exceptions import PermissionDenied


class TestVolunteerChangestate(TestCase):
    '''Tests for volunteer_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.volunteer = VolunteerFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')

    def test_volunteer_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        request = self.factory.get(
            'volunteer/changestate/%d' % self.volunteer.pk)
        request.user = self.privileged_user
        response = volunteer_changestate(request, self.volunteer.pk)
        nt.assert_equal(response.status_code, 302)

    @nt.raises(PermissionDenied)
    def test_volunteer_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        request = self.factory.get(
            'volunteer/changestate/%d' % self.volunteer.pk)
        request.user = ProfileFactory().user_object
        response = volunteer_changestate(request, self.volunteer.pk)
