import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.exceptions import PermissionDenied
from datetime import datetime
import pytz
from gbe.views import assign_volunteer
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    VolunteerFactory,
    ConferenceFactory,
    GenericEventFactory,
    UserFactory,
    VolunteerWindowFactory,
)
from tests.functions.gbe_functions import login_as
from scheduler.models import Event as sEvent


class TestAssignVolunteer(TestCase):
    '''Tests for review_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.privileged_profile = ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        group, nil = Group.objects.get_or_create(name='Volunteer Coordinator')
        self.privileged_user.groups.add(group)

    @nt.raises(PermissionDenied)
    def test_assign_volunteers_bad_user(self):
        ''' user does not have Volunteer Coordinator, permission is denied'''
        volunteer = VolunteerFactory.create()
        request = self.factory.get('volunteer/assign/%d' % volunteer.pk)
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = assign_volunteer(request, volunteer.pk)

    @nt.raises(PermissionDenied)
    def test_assign_volunteers_no_profile(self):
        ''' user does not have a profile, permission is denied'''
        volunteer = VolunteerFactory.create()
        request = self.factory.get('volunteer/assign/%d' % volunteer.pk)
        request.user = UserFactory.create()
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = assign_volunteer(request, volunteer.pk)

    def test_assign_volunteer_no_events(self):
        ''' assign a volunteer when there are no opportunities'''
        volunteer = VolunteerFactory.create()
        request = self.factory.get('volunteer/assign/%d' % volunteer.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = assign_volunteer(request, volunteer.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Assign Volunteer to Opportunities' in response.content)

    def test_assign_volunteer_show_current_events(self):
        '''only current conference events, and windows should be shown'''
        # horrible setup process. Need to fix
        current_conference = ConferenceFactory.create(
            accepting_bids=True)
        past_conference = ConferenceFactory.create(
            status='completed')
        current_opportunity = GenericEventFactory.create(
            conference=current_conference)
        past_opportunity = GenericEventFactory.create(
            conference=past_conference)
        current_opportunity.save()
        past_opportunity.save()

        current_sched = sEvent(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 5, 12, 0, 0, 0, pytz.utc),
            max_volunteer=10)
        current_sched.save()

        past_sched = sEvent(
            eventitem=past_opportunity,
            starttime=datetime(2015, 2, 25, 12, 0, 0, 0, pytz.utc),
            max_volunteer=10)
        past_sched.save()

        current_window = VolunteerWindowFactory.create(
            day__conference=current_conference)
        past_window = VolunteerWindowFactory.create(
            day__conference=past_conference)
        current_window.save()
        past_window.save()

        volunteer = VolunteerFactory.create(
            conference=current_conference,
            submitted=True,
            )
        volunteer.save()
        unavail_window = VolunteerWindowFactory.create(
            day__conference=current_conference)
        volunteer.available_windows.add(current_window)
        volunteer.unavailable_windows.add(unavail_window)

        request = self.factory.get('volunteer/assign/%d' % volunteer.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = assign_volunteer(request, volunteer.pk)

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Assign Volunteer to Opportunities' in response.content)
        nt.assert_true(volunteer.profile.display_name in response.content)
        nt.assert_true(str(volunteer.number_shifts) in response.content)
        nt.assert_true("Security/usher" in response.content)
        nt.assert_true(volunteer.opt_outs in response.content)
        nt.assert_true(str(volunteer.pre_event) in response.content)
        nt.assert_true(volunteer.background in response.content)

        nt.assert_true(str(current_opportunity) in response.content)
        nt.assert_false(str(past_opportunity) in response.content)
        nt.assert_true(
            current_sched.start_time.strftime(
                "%a, %-I %p") in response.content)
        nt.assert_true(
            current_sched.end_time.strftime("%a, %-I %p") in response.content)
        nt.assert_false(
            past_sched.starttime.strftime("%a, %-I %p") in response.content)
        # check for volunteer window
        nt.assert_true("10 AM - 2 PM" in response.content)
        nt.assert_true(str(current_sched.max_volunteer) in response.content)
