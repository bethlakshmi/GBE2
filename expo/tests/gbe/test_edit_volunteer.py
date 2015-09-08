from django.core.exceptions import PermissionDenied
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.contrib.auth.models import Group
from gbe.views import edit_volunteer
import mock
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (login_as,
                                           is_login_page,
                                           is_profile_update_page,
                                           location)


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
        group, nil = Group.objects.get_or_create(name='Volunteer Coordinator')
        self.privileged_user.groups.add(group)

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

#    def test_volunteer_edit_post_form_not_valid(self):
#        '''volunteer_edit, if form not valid, should return
#        to VolunteerEditForm'''
#        volunteer = factories.VolunteerFactory.create()
#        request = self.factory.get('/volunteer/edit/%d' % volunteer.pk)
#        request.user = self.privileged_user
#        request.POST = {}
#        request.POST.update(self.get_volunteer_form())
#        response = edit_volunteer(request, volunteer.pk)
#        nt.assert_equal(response.status_code, 200)
#        nt.assert_true('Edit Your Volunteer Proposal' in response.content)

#    def test_volunteer_edit_post_form_valid(self):
#        '''volunteer_edit, if form not valid, should return to ActEditForm'''
#        volunteer = factories.VolunteerFactory.create()
#        request = self.factory.get('/volunteer/edit/%d' % volunteer.pk)
#        request.user = self.privileged_user
#        request.POST = {}
#        request.POST.update(self.get_volunteer_form())
#        nt.set_trace()
#        response = edit_volunteer(request, volunteer.pk)
#        nt.assert_equal(response.status_code, 302)

#    def test_edit_bid_not_post(self):
#        '''edit_bid, not post, should take us to edit process'''
#        volunteer = factories.VolunteerFactory.create()
#        request = self.factory.get('/volunteer/edit/%d' % volunteer.pk)
#        request.user = self.privileged_user
#        response = edit_volunteer(request, volunteer.pk)
#        nt.assert_equal(response.status_code, 200)
#        nt.assert_true('Edit Your Volunteer Proposal' in response.content)
