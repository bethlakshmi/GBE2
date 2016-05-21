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
    is_login_page,
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
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Change Bid State:' in response.content)

    def test_review_volunteer_get_conference(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': volunteer.conference.id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
        self.assertTrue('Review Information' in response.content)

    def test_review_volunteer_coordinator(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Change Bid State:' in response.content)
        self.assertTrue('Bid Information' in response.content)
        self.assertTrue('Review Information' in response.content)

    def test_review_volunteer_post_invalid(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        data = self.get_form(volunteer, self.coordinator, invalid=True)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Change Bid State:' in response.content)
        self.assertTrue('Bid Information' in response.content)

    def test_review_volunteer_post_valid(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        data = self.get_form(volunteer, self.coordinator)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        html_tag = '<h2 class="review-title">%s</h2>'
        title_string = ("Bid Information for %s" %
                        volunteer.conference.conference_name)
        html_title = html_tag % title_string
        assert html_title in response.content

    def test_review_volunteer_past_conference(self):
        conference = ConferenceFactory(status='completed')
        volunteer = VolunteerFactory(conference=conference)
        url = reverse(self.view_name, args=[volunteer.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[volunteer.pk]))
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Review Information' in response.content)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
