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
        ConferenceDayFactory(conference=self.context.conference,
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
            'e_conference': self.context.conference.pk,
            'max_volunteer': 1,
            'day': self.day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'set_event': 'Any value',
            'alloc_0-role': 'Teacher',
            'alloc_1-role': 'Volunteer',
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
        self.assertContains(response, self.context.show.e_title)
        self.assertContains(response, self.context.show.e_description)
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                self.context.days[0].pk,
                self.context.days[0].day.strftime(DATE_FORMAT)
        ))
        self.assertContains(response,
                            'name="max_volunteer" type="number" value="7" />')
        self.assertContains(
            response,
            'name="duration" step="any" type="number" value="1.5" />')

    def test_authorized_user_can_also_get_volunteer_mgmt(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteer Management")
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

'''
    def test_authorized_user_can_access_special(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "special"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=special"
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assert_event_was_picked_in_wizard(response, "special")
        self.assert_role_choice(response, "Staff Lead")
        self.assertNotContains(response, "Continue to Volunteer Opportunities")


    def test_auth_user_basic_scheduling(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'Make New Class')
        self.assertContains(
            response,
            'type="number" value="1"')


    def test_create_master(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_class = GenericEvent.objects.get(e_title=data['e_title'])
        self.assertEqual(new_class.type, "Master")
        occurrence = Event.objects.get(
            eventitem__eventitem_id=new_class.eventitem_id)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%dL]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.day.day.strftime(DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

    def test_create_master_w_staffing(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['alloc_0-worker'] = self.teacher.pk
        data['alloc_1-worker'] = self.privileged_user.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_class = GenericEvent.objects.get(e_title=data['e_title'])
        occurrence = Event.objects.get(
            eventitem__eventitem_id=new_class.eventitem_id)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%dL]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.day.day.strftime(DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

    def test_create_dropin_w_staffing(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "drop-in"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=drop-in"
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['type'] = "Drop-In"
        data['alloc_0-role'] = "Staff Lead"
        data['alloc_1-role'] = "Teacher"
        data['alloc_2-role'] = "Volunteer"
        data['alloc_0-worker'] = self.privileged_user.pk
        data['alloc_1-worker'] = self.teacher.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_class = GenericEvent.objects.get(e_title=data['e_title'])
        self.assertEqual(new_class.type, "Drop-In")
        occurrence = Event.objects.get(
            eventitem__eventitem_id=new_class.eventitem_id)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%dL]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.day.day.strftime(DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

    def test_create_show_w_staffing(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "show"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=show"
        login_as(self.privileged_user, self)
        data = self.edit_class()
        
        data.pop('type', None)
        data['alloc_0-role'] = "Producer"
        data['alloc_1-role'] = "Technical Director"
        data['alloc_0-worker'] = self.privileged_user.pk
        data['alloc_1-worker'] = self.teacher.performer_profile.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_show = Show.objects.get(e_title=data['e_title'])
        occurrence = Event.objects.get(
            eventitem__eventitem_id=new_show.eventitem_id)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%dL]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.day.day.strftime(DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

    def test_create_special_w_staffing(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "special"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=special"
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['type'] = "Special"
        data['alloc_0-role'] = "Staff Lead"
        data['alloc_0-worker'] = self.teacher.performer_profile.pk
        data.pop('alloc_1-role', None)
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_event = GenericEvent.objects.get(e_title=data['e_title'])
        self.assertEqual(new_event.type, "Special")
        occurrence = Event.objects.get(
            eventitem__eventitem_id=new_event.eventitem_id)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%dL]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['e_title'],
                self.day.day.strftime(DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="bid-table success">\n       ' +
            '<td class="bid-table">%s</td>' % data['e_title'])

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
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
        data = self.edit_class()
        data['location'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")

    def test_auth_user_bad_generic_booking_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['e_title'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "This field is required.")
'''
