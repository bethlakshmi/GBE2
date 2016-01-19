from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_volunteer_list
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    VolunteerFactory,
    VolunteerWindowFactory)
from tests.factories.scheduler_factories import ResourceAllocationFactory
from tests.functions.gbe_functions import login_as
from django.core.exceptions import PermissionDenied
from gbe.models import ProfilePreferences
from scheduler.models import Event as sEvent
from datetime import datetime, date, time
import pytz
from scheduler.models import (
    Worker,
    EventContainer
)


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

    def test_review_volunteer_has_commitments(self):
        ''' when a volunteer is already booked somewhere, it should show up'''

        current_opportunity = GenericEventFactory.create(
            conference=self.volunteer.conference,
            volunteer_category='VA1',
            type='Volunteer')
        current_opportunity.save()
        booked_sched = sEvent(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc),
            max_volunteer=1)
        booked_sched.save()
        worker = Worker(_item=self.volunteer.profile, role='Volunteer')
        worker.save()
        volunteer_assignment = ResourceAllocationFactory.create(
            event=booked_sched,
            resource=worker
        )

        request = self.factory.get('volunteer/review/?conf_slug=%s' %
                                   self.volunteer.conference.conference_slug)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_volunteer_list(request)
        print(response)

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_equal(
            response.content.count(str(current_opportunity)),
            1,
            msg="The commitment %s is not showing up" % (
                str(current_opportunity)))
        nt.assert_in(
            booked_sched.start_time.strftime("%a, %b %d, %-I:%M %p"),
            response.content,
            msg="start time for commitment (%s) didn't show up" % (
                booked_sched.start_time.strftime("%a, %b %d, %-I:%M %p")))
        nt.assert_in(
            booked_sched.end_time.strftime("%-I:%M %p"),
            response.content,
            msg="end time for commitment (%s) didn't show up" % (
                booked_sched.end_time.strftime("%-I:%M %p")))

    def test_review_volunteer_has_old_commitments(self):
        ''' when a volunteer is booked in old conference, it should not show'''
        past_conference = ConferenceFactory.create(
            accepting_bids=False,
            status='completed'
            )
        past_opportunity = GenericEventFactory.create(
            conference=past_conference,
            volunteer_category='VA1',
            type='Volunteer')
        past_opportunity.save()
        booked_sched = sEvent(
            eventitem=past_opportunity,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc),
            max_volunteer=1)
        booked_sched.save()
        worker = Worker(_item=self.volunteer.profile, role='Volunteer')
        worker.save()
        volunteer_assignment = ResourceAllocationFactory.create(
            event=booked_sched,
            resource=worker
        )

        request = self.factory.get('volunteer/review/?conf_slug=%s' %
                                   self.volunteer.conference.conference_slug)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_volunteer_list(request)

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_false(str(past_opportunity) in response.content,
                        msg="The commitment %s is showing up" % (
                            str(past_opportunity)))

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
