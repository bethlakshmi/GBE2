from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
)
from tests.factories.ticketing_factories import BrownPaperEventsFactory
from scheduler.models import Event
from gbe.models import GenericEvent
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
from gbetext import (
    create_ticket_event_success_msg,
    link_event_to_ticket_success_msg,
    no_tickets_found_msg,
)


class TestTicketedClassWizard(TestCase):
    '''This view makes Master and Drop In and associates them w. tickets'''
    view_name = 'create_ticketed_class_wizard'

    def setUp(self):
        self.room = RoomFactory()
        self.teacher = PersonaFactory()
        self.current_conference = ConferenceFactory(accepting_bids=True)
        self.day = ConferenceDayFactory(conference=self.current_conference)
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "master"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=master"
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def get_data(self):
        data = {
            'accepted_class': self.test_class.pk,
            'pick_class': 'Next'
        }
        return data

    def edit_class(self):
        data = {
            'type': 'Master',
            'e_title': "Test Class Wizard",
            'e_description': 'Description',
            'e_conference': self.current_conference.pk,
            'max_volunteer': 1,
            'day': self.day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'set_class': 'Finish',
            'alloc_0-role': 'Teacher',
            'alloc_1-role': 'Volunteer',
        }
        return data

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access_master(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assert_event_was_picked_in_wizard(response, "master")
        self.assertContains(
            response,
            '<option value="%s" selected="selected">%s</option>' % (
                'Teacher',
                'Teacher'))
        self.assertContains(
            response,
            '<option value="%s" selected="selected">%s</option>' % (
                'Volunteer',
                'Volunteer'))

    def test_authorized_user_can_access_dropin(self):
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug, "drop-in"],
            urlconf='gbe.scheduling.urls'
            ) + "?pick_event=Next&event_type=drop-in"
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assert_event_was_picked_in_wizard(response, "drop-in")
        self.assertContains(
            response,
            '<option value="%s" selected="selected">%s</option>' % (
                'Teacher',
                'Teacher'))
        self.assertContains(
            response,
            '<option value="%s" selected="selected">%s</option>' % (
                'Volunteer',
                'Volunteer'))
        self.assertContains(
            response,
            '<option value="%s" selected="selected">%s</option>' % (
                'Staff Lead',
                'Staff Lead'))

    def test_authorized_user_can_access_master_no_tickets(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Set Tickets for Event")

    def test_authorized_user_can_access_master_and_tickets(self):
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set Tickets for Event")

    def test_auth_user_basic_scheduling(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            'Make New Class')
        self.assertContains(
            response,
            'type="number" value="1"')
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (
                self.day.pk,
                self.day.day.strftime(DATE_FORMAT)
            ))

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

    def test_get_tickets(self):
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        bpt_event = BrownPaperEventsFactory(
            conference=self.current_conference)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "%s - %s" % (bpt_event.bpt_event_id,
                                                   bpt_event.title))

    def test_set_ticket(self):
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        bpt_event = BrownPaperEventsFactory(
            conference=self.current_conference)
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['bpt_events'] = bpt_event.pk
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
            link_event_to_ticket_success_msg + '%s - %s, ' % (
                bpt_event.bpt_event_id,
                bpt_event.title)
            )
