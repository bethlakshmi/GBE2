import nose.tools as nt
from django.test import TestCase
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
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')
        self.coordinator = ProfileFactory()
        grant_privilege(self.coordinator, 'Volunteer Reviewers')
        grant_privilege(self.coordinator, 'Volunteer Coordinator')

    def get_form(self, bid, evaluator, invalid=False):
        data = {'vote': 3,
                'notes': "Foo",
                'bid': bid.pk,
                'evaluator': evaluator.pk}
        if invalid:
            del(data['vote'])
        return data

    def test_review_volunteer_all_well(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_false('Change Bid State:' in response.content)

    def test_review_volunteer_get_conference(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': volunteer.conference.id})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_false('Change Bid State:' in response.content)

    def test_review_volunteer_coordinator(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Change Bid State:' in response.content)
        nt.assert_true('Bid Information' in response.content)

    def test_review_volunteer_post_invalid(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        data = self.get_form(volunteer, self.coordinator, invalid=True)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Change Bid State:' in response.content)
        nt.assert_true('Bid Information' in response.content)

    def test_review_volunteer_post_valid(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        data = self.get_form(volunteer, self.coordinator)
        response = self.client.post(url, data=data, follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Review Volunteers' in response.content)
        nt.assert_true('Bid Information' in response.content)
