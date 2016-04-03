import nose.tools as nt
from django.core.exceptions import PermissionDenied
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    VolunteerFactory
)
from tests.functions.gbe_functions import (
    current_conference,
    login_as,
)


class TestViewVolunteer(TestCase):
    '''Tests for view_volunteer view'''
    view_name = 'volunteer_view'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.conference = current_conference()

    def test_view_act_all_well(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(volunteer.profile, self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)

    def test_view_act_wrong_profile(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 403)
#        nt.assert_true(test_string in response.content)
