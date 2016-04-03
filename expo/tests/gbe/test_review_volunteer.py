import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    VolunteerFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestReviewVolunteer(TestCase):
    '''Tests for review_volunteer view'''
    view_name = 'volunteer_review'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

    def test_review_volunteer_all_well(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
