import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    VolunteerWindowFactory,
)
from tests.functions.gbe_functions import login_as
from gbe.models import Conference


class TestCreateVolunteer(TestCase):
    '''Tests for create_volunteer view'''
    view_name = 'volunteer_create'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        Conference.objects.all().delete()
        self.conference = ConferenceFactory(accepting_bids=True)
        days = ConferenceDayFactory.create_batch(2, conference=self.conference)
        [VolunteerWindowFactory(day=day) for day in days]

    def get_volunteer_form(self, submit=False, invalid=False):
        form = {'profile': 1,
                'number_shifts': 2,
                'interests': ['VA0'],
                'available_windows': self.conference.windows().values_list(
                    'pk', flat=True)
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['number_shifts'])
        return form

    def test_create_volunteer_no_profile(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_create_volunteer_post_no_profile(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        data = self.get_volunteer_form()
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)

    def test_create_volunteer_post_valid_form(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        data = self.get_volunteer_form()
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)

    def test_create_volunteer_post_form_invalid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        data = self.get_volunteer_form(invalid=True)
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 200)

    def test_create_volunteer_no_post(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.post(url)
        nt.assert_equal(response.status_code, 200)
