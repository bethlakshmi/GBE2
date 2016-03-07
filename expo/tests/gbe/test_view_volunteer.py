import nose.tools as nt
from django.core.exceptions import PermissionDenied
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_volunteer
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    VolunteerFactory
)
import mock


class TestViewVolunteer(TestCase):
    '''Tests for view_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()

    def test_view_act_all_well(self):
        volunteer = VolunteerFactory.create()
        request = self.factory.get('volunteer/view/%d' % volunteer.pk)
        request.user = volunteer.profile.user_object
        request.session = {'cms_admin_site': 1}
        response = view_volunteer(request, volunteer.pk)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)

    @nt.raises(PermissionDenied)
    def test_view_act_wrong_profile(self):
        volunteer = VolunteerFactory.create()
        request = self.factory.get('volunteer/view/%d' % volunteer.pk)
        request.user = ProfileFactory().user_object
        request.session = {'cms_admin_site': 1}
        response = view_volunteer(request, volunteer.pk)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)
