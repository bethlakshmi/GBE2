from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory,
    VolunteerWindowFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as
)
from gbetext import (
    default_volunteer_submit_msg,
    default_volunteer_no_bid_msg
)
from gbe.models import (
    AvailableInterest,
    Conference,
    Volunteer,
    UserMessage
)


class TestCreateVolunteer(TestCase):
    '''Tests for create_volunteer view'''
    view_name = 'volunteer_create'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        Conference.objects.all().delete()
        UserMessage.objects.all().delete()
        AvailableInterest.objects.all().delete()
        self.conference = ConferenceFactory(accepting_bids=True)
        days = ConferenceDayFactory.create_batch(3, conference=self.conference)
        [VolunteerWindowFactory(day=day) for day in days]
        self.interest = AvailableInterestFactory()

    def get_volunteer_form(self, submit=False, invalid=False):
        form = {'profile': 1,
                'number_shifts': 2,
                'interests': ['VA0'],
                'available_windows': self.conference.windows().values_list(
                    'pk', flat=True)[0:2],
                'unavailable_windows': self.conference.windows().values_list(
                    'pk', flat=True)[2],
                '%d-rank' % self.interest.pk: 4,
                '%d-interest' % self.interest.pk: self.interest.pk
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['number_shifts'])
        return form

    def post_volunteer_submission(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        num_volunteers_before = Volunteer.objects.count()
        data = self.get_volunteer_form(submit=True)
        response = self.client.post(url, data=data, follow=True)
        return response, num_volunteers_before

    def test_create_volunteer_no_profile(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_create_volunteer_post_no_profile(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        data = self.get_volunteer_form()
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_create_volunteer_post_valid_form(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        data = self.get_volunteer_form()
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_create_volunteer_post_form_invalid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        data = self.get_volunteer_form(invalid=True)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_create_volunteer_no_post(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_create_volunteer_post_with_submit_is_true(self):
        response, num_volunteers_before = self.post_volunteer_submission()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Profile View', response.content)
        self.assertEqual(num_volunteers_before + 1, Volunteer.objects.count())

    def test_create_volunteer_with_get_request(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Volunteer', response.content)

    def test_volunteer_submit_make_message(self):
        response, data = self.post_volunteer_submission()
        print response.content
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_volunteer_submit_msg)

    def test_volunteer_submit_has_message(self):
        msg = UserMessageFactory(
            view='CreateVolunteerView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_volunteer_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_no_biddable_conference(self):
        self.conference.accepting_bids = False
        self.conference.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_bid_msg)

    def test_no_window_for_conference(self):
        Conference.objects.all().delete()
        ConferenceFactory(accepting_bids=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_bid_msg)

