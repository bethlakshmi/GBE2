from django.core import mail
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    VolunteerFactory,
    ProfilePreferencesFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.core.exceptions import PermissionDenied
from tests.contexts import StaffAreaContext
from gbe.models import Conference
from gbe.functions import get_current_conference
from expo.settings import (
    DATETIME_FORMAT,
    TIME_FORMAT,
    DATE_FORMAT,
)
from django.utils.formats import date_format

class TestVolunteerChangestate(TestCase):
    '''Tests for volunteer_changestate view'''
    view_name = 'volunteer_changestate'

    def setUp(self):
        Conference.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.volunteer = VolunteerFactory(submitted=True)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

    def test_volunteer_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_volunteer_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_volunteer_changestate_authorized_user_post(self):
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.conference,
                'events': [],
                'accepted': 3}
        response = self.client.post(url, data=data)
        nt.assert_equal(response.status_code, 302)

    def test_volunteer_changestate_sends_notification(self):
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.conference,
                'events': [],
                'accepted': 3}
        response = self.client.post(url, data=data)
        assert 1 == len(mail.outbox)
        msg = mail.outbox[0]
        expected_subject = "A change has been made to your Volunteer Schedule!"
        assert msg.subject == expected_subject

    def test_volunteer_changestate_gives_overbook_warning(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        context = StaffAreaContext(
            staff_lead=self.volunteer.profile,
            conference=self.volunteer.conference)
        opp = context.add_volunteer_opp()
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.conference,
                'events': [opp.pk],
                'accepted': 3}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, "Found event conflict")

    def test_volunteer_changestate_gives_event_over_full_warning(self):
        ProfilePreferencesFactory(profile=self.volunteer.profile)
        context = StaffAreaContext(
            conference=self.volunteer.conference)
        opp = context.add_volunteer_opp()
        context.book_volunteer(
            volunteer_sched_event=opp,
            volunteer=context.staff_lead)
        url = reverse(self.view_name,
                      args=[self.volunteer.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'conference': self.volunteer.conference,
                'events': [opp.pk],
                'accepted': 3}
        response = self.client.post(url, data=data, follow=True)
        self.assertContains(response, "Over by 1 volunteer.")
