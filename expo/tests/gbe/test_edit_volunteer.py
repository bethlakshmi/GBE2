from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.http import Http404
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.contrib.auth.models import Group
from gbe.views import edit_volunteer
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (
    login_as,
    grant_privilege,
)


class TestEditVolunteer(TestCase):
    '''Tests for edit_volunteer view'''

    # this test case should be unnecessary, since edit_volunteer should go away
    # for now, test it.

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        self.privileged_profile = factories.ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')

    def get_volunteer_form(self, submit=False, invalid=False):
        form = {'profile': 1,
                'number_shifts': 2,
                'availability': ('SH0',),
                'interests': ('VA0',),
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['number_shifts'])
        return form

    @nt.raises(PermissionDenied)
    def test_edit_volunteer_no_volunteer(self):
        '''Should get 404 if no valid volunteer ID'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/volunteer/edit/-1')
        request.user = profile.user_object
        response = edit_volunteer(request, -1)

    @nt.raises(PermissionDenied)
    def test_edit_volunteer_profile_is_not_coordinator(self):
        user = factories.ProfileFactory.create().user_object
        volunteer = factories.VolunteerFactory.create()
        request = self.factory.get('/volunteer/edit/%d' % volunteer.pk)
        request.user = user
        response = edit_volunteer(request, volunteer.pk)

    def test_volunteer_edit_post_form_not_valid(self):
        '''volunteer_edit, if form not valid, should return
        to VolunteerEditForm'''
        volunteer = factories.VolunteerFactory.create()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(
            url,
            self.get_volunteer_form(invalid=True))

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Volunteer Bid' in response.content)


    def test_volunteer_edit_get(self):
        volunteer = factories.VolunteerFactory(
            availability='',
            unavailability='',
            interests='')
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Volunteer Bid' in response.content)
