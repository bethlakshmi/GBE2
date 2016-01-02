from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_volunteer_list
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    VolunteerFactory,
    VolunteerWindowFactory)
from tests.functions.gbe_functions import login_as
from django.core.exceptions import PermissionDenied
from gbe.models import ProfilePreferences

class TestReviewVolunteerList(TestCase):
    '''Tests for review_volunteer_list view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.privileged_profile = ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        group, nil = Group.objects.get_or_create(name='Volunteer Reviewers')
        self.privileged_user.groups.add(group)

        self.volunteer = VolunteerFactory.create()
        self.avail_window = VolunteerWindowFactory.create()
        self.unavail_window = VolunteerWindowFactory.create()
        self.volunteer.available_windows.add(self.avail_window)
        self.volunteer.unavailable_windows.add(self.unavail_window)
        self.volunteer.submitted = True
        self.volunteer.save()
        self.volunteer.profile.user_object.email = "review_vol@testemail.com"
        self.volunteer.profile.user_object.save()
        self.prefs = ProfilePreferences()
        self.prefs.profile = self.volunteer.profile
        self.prefs.in_hotel = "Maybe"
        self.prefs.inform_about = True
        self.prefs.show_hotel_infobox = True
        self.prefs.save()


    def test_review_volunteer_all_well(self):
        '''default conference selected, make sure it returns the right page'''
        request = self.factory.get('volunteer/review/')
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_volunteer_list(request)
        
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_volunteer_w_conf(self):
        ''' when a specific conf has specific bids, check bid details'''
        volunteer = VolunteerFactory.create()
        avail_window = VolunteerWindowFactory.create()
        unavail_window = VolunteerWindowFactory.create()
        volunteer.available_windows.add(avail_window)
        volunteer.unavailable_windows.add(unavail_window)
        volunteer.submitted = True
        volunteer.save()
        volunteer.profile.user_object.email = "review_vol@testemail.com"
        volunteer.profile.user_object.save()
        prefs = ProfilePreferences()
        prefs.profile = volunteer.profile
        prefs.in_hotel = "Maybe"
        prefs.inform_about = True
        prefs.show_hotel_infobox = True
        prefs.save()

        request = self.factory.get('volunteer/review/?conf_slug=%s' %
                                   self.volunteer.conference.conference_slug)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_volunteer_list(request)
        
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_true(str(self.volunteer.number_shifts) in response.content)
        nt.assert_true(self.volunteer.background in response.content)
        nt.assert_true(self.volunteer.profile.display_name in response.content)
        nt.assert_true(
            self.volunteer.profile.user_object.email in response.content)
        nt.assert_true(self.prefs.in_hotel in response.content)
        nt.assert_true(unicode(self.avail_window) in response.content)
        nt.assert_true(unicode(self.unavail_window) in response.content)
        nt.assert_true("No Decision" in response.content)
        nt.assert_true("Review" in response.content)

    def test_review_volunteer_as_coordinator(self):
        ''' volunteer coordinators get special privileges'''
        coord_profile = ProfileFactory.create()
        group, nil = Group.objects.get_or_create(name='Volunteer Reviewers')
        group2, nil = Group.objects.get_or_create(name='Volunteer Coordinator')
        coord_profile.user_object.groups.add(group)
        coord_profile.user_object.groups.add(group2)

        request = self.factory.get('volunteer/review/?conf_slug=%s' %
                                   self.volunteer.conference.conference_slug)
        request.user = coord_profile.user_object
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_volunteer_list(request)
        
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_true(str(self.volunteer.number_shifts) in response.content)
        nt.assert_true(self.volunteer.background in response.content)
        nt.assert_true(self.volunteer.profile.display_name in response.content)
        nt.assert_true(
            self.volunteer.profile.user_object.email in response.content)
        nt.assert_true(self.prefs.in_hotel in response.content)
        nt.assert_true(unicode(self.avail_window) in response.content)
        nt.assert_true(unicode(self.unavail_window) in response.content)
        nt.assert_true("No Decision" in response.content)
        nt.assert_true("Review" in response.content)
        nt.assert_true("Assign" in response.content)
        nt.assert_true("Edit" in response.content)

    @nt.raises(PermissionDenied)
    def test_review_volunteer_bad_user(self):
        ''' user does not have the right privilege and permission is denied'''
        request = self.factory.get('volunteer/review/')
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_volunteer_list(request)

    @nt.raises(PermissionDenied)
    def test_review_volunteer_no_profile(self):
        ''' user does not have a profile, gets permission denied'''
        request = self.factory.get('volunteer/review/')
        request.user = UserFactory.create()
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_volunteer_list(request)
