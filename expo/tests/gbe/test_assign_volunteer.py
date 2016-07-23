import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.exceptions import PermissionDenied
from datetime import datetime, date, time
from django.core.urlresolvers import reverse
import pytz
import re
from tests.factories.gbe_factories import (
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    VolunteerFactory,
    VolunteerWindowFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from scheduler.models import Event as sEvent
from scheduler.models import (
    Worker,
    ResourceAllocation,
    EventContainer
)
from tests.contexts import VolunteerContext

class TestAssignVolunteer(TestCase):
    '''Tests for review_volunteer view'''
    view_name = 'volunteer_assign'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

    def test_assign_volunteers_bad_user(self):
        ''' user does not have Volunteer Coordinator, permission is denied'''
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(403, response.status_code)

    def test_assign_volunteers_no_profile(self):
        ''' user does not have a profile, permission is denied'''
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(403, response.status_code)

    def test_assign_volunteers_old_bid(self):
        ''' bid is froma past conference'''
        context = VolunteerContext()
        context.conference.status = 'past'
        context.conference.save()
        url = reverse(self.view_name,
                      args=[context.bid.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertRedirects(response, reverse(
            'volunteer_view',
            urlconf='gbe.urls',
            args=[context.bid.pk]))

    def test_assign_volunteer_show_current_events(self):
        '''only current conference events, and windows should be shown'''
        # horrible setup process. Need to fix
        current_conference = ConferenceFactory(
            accepting_bids=True)
        past_conference = ConferenceFactory(
            status='completed')

        parent = GenericEventFactory(
            conference=current_conference)
        parent.save()
        current_opportunity = GenericEventFactory(
            conference=current_conference,
            volunteer_category='VA1',
            type='Volunteer')
        current_opportunity.save()
        rehearsal = GenericEventFactory(
            conference=current_conference,
            type="Rehearsal Slot")
        rehearsal.save()
        past_opportunity = GenericEventFactory(
            conference=past_conference)
        past_opportunity.save()

        parent_sched = sEvent(
            eventitem=parent,
            starttime=datetime(2016, 2, 5, 12, 0, 0, 0, pytz.utc))
        parent_sched.save()
        current_sched = sEvent(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 5, 12, 0, 0, 0, pytz.utc),
            max_volunteer=10)
        current_sched.save()
        container = EventContainer(
            parent_event=parent_sched,
            child_event=current_sched
        )
        container.save()

        booked_sched = sEvent(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc),
            max_volunteer=1)
        booked_sched.save()

        unavail_sched = sEvent(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 7, 12, 0, 0, 0, pytz.utc),
            max_volunteer=10)
        unavail_sched.save()

        rehearsal_slot = sEvent(
            eventitem=rehearsal,
            starttime=datetime(2016, 2, 6, 13, 0, 0, 0, pytz.utc),
            max_volunteer=10)
        rehearsal_slot.save()

        past_sched = sEvent(
            eventitem=past_opportunity,
            starttime=datetime(2015, 2, 25, 12, 0, 0, 0, pytz.utc),
            max_volunteer=10)
        past_sched.save()

        current_window = VolunteerWindowFactory(
            day__conference=current_conference)
        unavail_window = VolunteerWindowFactory(
            day__conference=current_conference,
            day__day=date(2016, 2, 7),
            start=time(11),
            end=time(15))
        past_window = VolunteerWindowFactory(
            day__conference=past_conference)
        current_window.save()
        past_window.save()

        volunteer = VolunteerFactory(
            conference=current_conference,
            submitted=True,
            )
        volunteer.save()
        volunteer.available_windows.add(current_window)
        volunteer.unavailable_windows.add(unavail_window)
        worker = Worker(_item=volunteer.profile, role='Volunteer')
        worker.save()
        volunteer_assignment = ResourceAllocation(
            event=booked_sched,
            resource=worker
        )
        volunteer_assignment.save()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf="gbe.urls")

        login_as(self.privileged_user, self)
        response = self.client.get(url)

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Assign Volunteer to Opportunities' in response.content)

        # volunteer details
        nt.assert_true(volunteer.profile.display_name in response.content)
        nt.assert_true(str(volunteer.number_shifts) in response.content)
        nt.assert_true("Security/usher" in response.content)
        nt.assert_true(volunteer.opt_outs in response.content)
        nt.assert_true(str(volunteer.pre_event) in response.content)
        nt.assert_true(volunteer.background in response.content)

        # event names
        nt.assert_equal(
            response.content.count(str(parent)),
            1,
            msg="There should be only 1 parent event")
        nt.assert_equal(
            response.content.count(str(current_opportunity)),
            3,
            msg="There should be 3 schedule items for current_opportunity")
        nt.assert_not_in(
            str(rehearsal),
            response.content,
            msg="Event Title for rehearsal should not")
        nt.assert_not_in(
            str(past_opportunity),
            response.content,
            msg="Event Title for past_opportunity should not show up")

        # start and end times
        nt.assert_in(
            current_sched.start_time.strftime("%a, %-I %p"),
            response.content,
            msg="start time for current_sched didn't show up")
        nt.assert_in(
            current_sched.end_time.strftime("%a, %-I %p"),
            response.content,
            msg="end time for current_sched didn't show up")
        nt.assert_in(
            booked_sched.start_time.strftime("%a, %-I %p"),
            response.content,
            msg="start time for booked_sched didn't show up")
        nt.assert_in(
            booked_sched.end_time.strftime("%a, %-I %p"),
            response.content,
            msg="end time for booked_sched didn't show up")
        nt.assert_in(
            unavail_sched.start_time.strftime("%a, %-I %p"),
            response.content,
            msg="start time for unavail_sched didn't show up")
        nt.assert_in(
            unavail_sched.end_time.strftime("%a, %-I %p"),
            response.content,
            msg="end time for unavail_sched didn't show up")
        nt.assert_not_in(
            past_sched.starttime.strftime("%a, %-I %p"),
            response.content,
            msg="start time for past_sched shouldn't show up")
        nt.assert_not_in(
            rehearsal_slot.starttime.strftime("%a, %-I %p"),
            response.content,
            msg="end time for past_sched shouldn't show up")

        # check for volunteer windows
        nt.assert_is_not_none(
            re.search("Fri,\s+10 AM -\s+2 PM", response.content),
            msg="current_window shows with current_sched is not found")
        nt.assert_is_not_none(
            re.search("Sun,\s+11 AM -\s+3 PM", response.content),
            msg="unavail_window shows with unavail_sched is not found")

        nt.assert_equal(
            response.content.count(
                '''<td class="bid-table">10</td>'''),
            2,
            msg="current_sched and unavail_sched should have 10 volunteers")

        # all three volunteer <-> event connections are present
        nt.assert_true(
            "Free<br>" in response.content,
            msg="The volunteer should be free for current_sched event")
        nt.assert_true(
            "Not Free<br>" in response.content,
            msg="The volunteer should be not free for unavail_sched event")
        nt.assert_equal(
            response.content.count("Interested<br>"),
            3,
            msg="volunteer vs. event interest did not match for 3 events")
        nt.assert_is_not_none(
            re.search(
                '''<td class="bid-table">\s+N\s+</td>''',
                response.content),
            msg="The current and unavailable events should be not yet full")
        nt.assert_is_not_none(
            re.search(
                '''<td class="bid-table">\s+Y\s+</td>''',
                response.content),
            msg="The booked event should show as full")

        # using \ to make sure the formatting of the reg ex is correct.
        checked_box = '''<input id="id_events_\d"\s+name="events"\s''' + \
            '''type="checkbox" value="''' + str(booked_sched.pk) + \
            '''"\s+checked="checked"/>'''
        nt.assert_is_not_none(re.search(
            checked_box,
            response.content),
            msg="The booked event should appear as checked in form")
