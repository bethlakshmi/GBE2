from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from scheduler.models import Event
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from tests.functions.gbe_scheduling_functions import (
    assert_event_was_picked_in_wizard,
    assert_good_sched_event_form_wizard,
)
from expo.settings import DATE_FORMAT


class TestRehearsalWizard(TestCase):
    '''Tests for the 2nd stage in the rehearsal wizard view'''
    view_name = 'rehearsal_wizard'

    def setUp(self):
        self.room = RoomFactory()
        self.show_volunteer = VolunteerContext()
        self.current_conference = self.show_volunteer.conference
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def create_opp(self):
        data = {
            'type': 'Volunteer',
            'e_conference': self.current_conference.pk,
            'e_title': "Test Volunteer Wizard #%d" % self.room.pk,
            'e_description': 'Description',
            'max_volunteer': 0,
            'day': self.special_volunteer.window.day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'alloc_0-role': 'Staff Lead',
            'alloc_0-worker': self.staff_area.staff_lead.pk,
            'set_opp': 'Finish',
        }
        return data

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assert_event_was_picked_in_wizard(response, "rehearsal")
        self.assertContains(response, str(self.show_volunteer.event.e_title))
        self.assertContains(response,
                            "Make New Show")

    def test_authorized_user_empty_conference(self):
        other_conf = ConferenceFactory()
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[other_conf.conference_slug],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url)
        self.assertNotContains(response,
                               str(self.show_volunteer.event.e_title))
        self.assertContains(response,
                            "Make New Show")

    def test_auth_user_can_pick_show(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_show': True,
                'show': self.show_volunteer.sched_event.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?rehearsal_open=True" % reverse(
                'edit_show',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      self.show_volunteer.sched_event.pk]))

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_show': True,
                'show': "boo"})
        self.assertContains(
            response,
            'Select a valid choice. boo is not one of the available choices.')

    def test_auth_user_pick_new_show(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_show': True,
                'show': ""},
            follow=True)
        self.assertRedirects(
            response,
            reverse('create_ticketed_event_wizard',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug,
                          "show"]))
