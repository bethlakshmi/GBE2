from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import create_volunteer
import mock
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    VolunteerWindowFactory,
)
from gbe.models import Conference


class TestCreateVolunteer(TestCase):
    '''Tests for create_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
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
        request = self.factory.get('volunteer/bid/')
        request.user = UserFactory.create()
        response = create_volunteer(request)
        nt.assert_equal(response.status_code, 302)

    def test_create_volunteer_post_no_profile(self):
        request = self.factory.post('volunteer/bid/')
        request.user = UserFactory.create()
        request.POST = self.get_volunteer_form()
        response = create_volunteer(request)
        nt.assert_equal(response.status_code, 302)

    def test_create_volunteer_post_valid_form(self):
        request = self.factory.post('volunteer/bid/')
        request.user = ProfileFactory().user_object
        request.POST = self.get_volunteer_form()
        request.session = {'cms_admin_site': 1}
        response = create_volunteer(request)
        # broken test: cannot create valid form

    def test_create_volunteer_post_form_invalid(self):
        request = self.factory.get('volunteer/bid/')
        request.method = 'POST'
        request.user = ProfileFactory.create().user_object
        request.POST = self.get_volunteer_form(invalid=True)
        request.session = {'cms_admin_site': 1}
        response = create_volunteer(request)
        nt.assert_equal(response.status_code, 200)

    def test_create_volunteer_no_post(self):
        request = self.factory.get('volunteer/bid/')
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}
        response = create_volunteer(request)
        nt.assert_equal(response.status_code, 200)
