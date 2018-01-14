from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    ProfileFactory,
    RoomFactory,
)
from scheduler.models import Event
from gbe.models import (
    GenericEvent,
    Show,
)
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
from tests.contexts import (
    ShowContext,
    VolunteerContext,
)
from gbe.duration import Duration
from datetime import timedelta


class TestEditEventView(TestCase):
    '''This view makes Master and Drop In and associates them w. tickets'''
    view_name = 'edit_event'

    def setUp(self):
        self.room = RoomFactory()
        self.context = ShowContext()
        self.context.sched_event.max_volunteer = 7
        self.context.sched_event.save()
        self.context.show.duration = Duration(hours=1, minutes=30)
        self.context.show.save()
        self.producer = self.context.set_producer()
        self.extra_day = ConferenceDayFactory(
            conference=self.context.conference,
            day=self.context.days[0].day + timedelta(days=1))
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def edit_event(self):
        data = {
            'type': 'Show',
            'e_title': "Test Event Wizard",
            'e_description': 'Description',
            'max_volunteer': 3,
            'day': self.extra_day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'set_event': 'Any value',
            'alloc_0-role': 'Producer',
            'alloc_1-role': 'Technical Director',
        }
        return data

    def assert_role_choice(self, response, role_type):
        self.assertContains(
            response,
            '<option value="%s" selected="selected">%s</option>' % (
                role_type,
                role_type))

    def test_edit_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access_show(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_role_choice(response, "Producer")
        self.assert_role_choice(response, "Technical Director")
        self.assertNotContains(response, "Volunteer Management")
        self.assertContains(response, "Finish")
        self.assertContains(response, self.context.show.e_title)
        self.assertContains(response, self.context.show.e_description)
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                self.context.days[0].pk,
                self.context.days[0].day.strftime(DATE_FORMAT)))
        self.assertContains(response,
                            'name="max_volunteer" type="number" value="7" />')
        self.assertContains(
            response,
            'name="duration" step="any" type="number" value="1.5" />')
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                self.producer.pk,
                str(self.producer)))

    def test_authorized_user_can_also_get_volunteer_mgmt(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteer Management")
        self.assertContains(response, "Save and Continue")
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                self.context.days[0].pk,
                self.context.days[0].day.strftime("%b. %-d, %Y")))
        self.assertContains(
            response,
            'name="new_opp-max_volunteer" type="number" value="7" />')
        self.assertContains(
            response,
            'name="new_opp-duration" type="text" value="01:30:00" />')

    def test_vol_opp_present(self):
        vol_context = VolunteerContext()
        vol_context.sched_event.max_volunteer = 7
        vol_context.sched_event.save()
        vol_context.opp_event.set_locations([])
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[vol_context.conference.conference_slug,
                  vol_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            'name="opp_event_id" type="hidden" value="%d" />' % (
                vol_context.opportunity.pk)
        )
        self.assertContains(
            response,
            'name="opp_sched_id" type="hidden" value="%d" />' % (
                vol_context.opp_event.pk)
        )
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                vol_context.window.day.pk,
                vol_context.window.day.day.strftime("%b. %-d, %Y")),
            2)
        self.assertContains(
            response,
            'name="max_volunteer" type="number" value="2" />')
        self.assertContains(
            response,
            'name="duration" type="text" value="01:00:00" />')

    def test_bad_conference(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=["BadConf",
                  self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_bad_occurrence_id(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk+1000],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1000))

    def test_edit_show_w_staffing(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['alloc_0-worker'] = self.privileged_user.profile.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%dL]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug]),
                self.context.conference.conference_slug,
                self.extra_day.pk,
                self.context.sched_event.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.extra_day.day.strftime(DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

    def test_edit_show_and_continue(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['edit_event'] = "Save and Continue"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            self.url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.extra_day.day.strftime(DATE_FORMAT))
            )
        self.assertContains(response, data['e_title'])
        self.assertContains(response, data['e_description'])
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                self.extra_day.pk,
                self.extra_day.day.strftime(DATE_FORMAT)))
        self.assertContains(response,
                            'name="max_volunteer" type="number" value="3" />')
        self.assertContains(
            response,
            'name="duration" step="any" type="number" value="2.5" />')

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['alloc_0-role'] = "bad role"
        data['alloc_1-role'] = "bad role"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "bad role is not one of the available choices.")

    def test_auth_user_bad_schedule_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['location'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")

    def test_auth_user_bad_generic_booking_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_event()
        data['e_title'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "This field is required.")

    def test_post_bad_occurrence(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk+1000],
            urlconf='gbe.scheduling.urls')
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1000))
