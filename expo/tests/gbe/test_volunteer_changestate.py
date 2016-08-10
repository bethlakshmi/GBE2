from django.core import mail
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    VolunteerFactory,
    ProfileFactory
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.core.exceptions import PermissionDenied


class TestVolunteerChangestate(TestCase):
    '''Tests for volunteer_changestate view'''
    view_name = 'volunteer_changestate'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.volunteer = VolunteerFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')

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
