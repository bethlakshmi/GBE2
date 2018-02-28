from django.test import TestCase
from django.test.client import RequestFactory
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


class TestVolunteerWizard(TestCase):
    '''Tests for the 2nd and 3rd stage in the volunteer wizard view'''
    view_name = 'create_volunteer_wizard'

    def setUp(self):
        self.room = RoomFactory()
        self.show_volunteer = VolunteerContext()
        self.current_conference = self.show_volunteer.conference
        self.special_volunteer = VolunteerContext(
            event=GenericEventFactory(
                e_conference=self.current_conference))
        self.staff_area = StaffAreaContext(
            conference=self.current_conference)
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assert_event_was_picked_in_wizard(response, "volunteer")
        print response
        self.assertContains(response, str(self.show_volunteer.event.e_title))
        self.assertContains(response,
                            str(self.special_volunteer.event.e_title))
        self.assertContains(response, str(self.staff_area.area.title))
        self.assertContains(response,
                            "Make a Volunteer Opportunity with no topic")

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
        self.assertNotContains(response,
                               str(self.special_volunteer.event.e_title))
        self.assertNotContains(response, str(self.staff_area.area.title))
        self.assertContains(response,
                            "Make a Volunteer Opportunity with no topic")

    def test_auth_user_can_pick_show(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': self.show_volunteer.sched_event.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?start_open=False" % reverse(
                'edit_event',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      self.show_volunteer.sched_event.pk]))

    def test_auth_user_can_pick_special(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': self.special_volunteer.sched_event.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?start_open=False" % reverse(
                'edit_event',
                urlconf='gbe.scheduling.urls',
                args=[self.current_conference.conference_slug,
                      self.special_volunteer.sched_event.pk]))

    def test_auth_user_can_pick_staff(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': "staff_%d" % self.staff_area.area.pk},
            follow=True)
        self.assertRedirects(
            response,
            "%s?start_open=False" % reverse(
                'edit_staff',
                urlconf='gbe.scheduling.urls',
                args=[self.staff_area.area.pk]))

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={
                'pick_topic': True,
                'volunteer_topic': "boo"})
        self.assertContains(
            response,
            'Select a valid choice. boo is not one of the available choices.')
'''
    def test_auth_user_pick_new_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        data['accepted_class'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            '<input checked="checked" id="id_accepted_class_0" ' +
            'name="accepted_class" type="radio" value="" />')
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
        self.assertContains(
            response,
            '<option value="%s" selected="selected">%s</option>' % (
                'Teacher',
                'Teacher'))

    def test_auth_user_load_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            'value="%s"' %
            self.test_class.b_title)
        self.assertContains(
            response,
            'type="number" value="1.0"')
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (
                self.day.pk,
                self.day.day.strftime(DATE_FORMAT)
            ))
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                self.test_class.teacher.pk,
                str(self.test_class.teacher)))

    def test_auth_user_load_panel(self):
        panel = ClassFactory(b_conference=self.current_conference,
                             e_conference=self.current_conference,
                             type="Panel",
                             accepted=3,
                             teacher=self.teacher,
                             submitted=True)
        login_as(self.privileged_user, self)
        data = self.get_data()
        data['accepted_class'] = panel.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            'value="%s"' %
            panel.b_title)
        self.assertContains(response, "Panelist")
        self.assertContains(response, "Moderator")
        self.assertContains(
            response,
            '<option value="%d" selected="selected">%s</option>' % (
                panel.teacher.pk,
                str(panel.teacher)))

    def test_auth_user_edit_class(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.filter(eventitem=self.test_class)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%dL]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence[0].pk))
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

    def test_auth_user_create_class(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['eventitem_id'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_class = Class.objects.get(e_title=data['e_title'])
        self.assertEqual(new_class.teacher, self.teacher)
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

    def test_auth_user_create_class_no_teacher(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['eventitem_id'] = ""
        data['alloc_0-worker'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            "You must select at least one person to run this class."
            )

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['alloc_0-role'] = "bad role"
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

    def test_auth_user_bad_class_booking_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['type'] = "bad type"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "bad type is not one of the available choices.")

    def test_get_class_recommendations(self):
        self.test_class.schedule_constraints = "[u'1']"
        self.test_class.avoided_constraints = "[u'2']"
        self.test_class.space_needs = "2"
        self.test_class.type = "Panel"
        self.test_class.save()
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        assert_good_sched_event_form_wizard(response, self.test_class)

    def test_get_empty_schedule_info(self):
        self.test_class.schedule_constraints = ""
        self.test_class.avoided_constraints = ""
        self.test_class.space_needs = ""
        self.test_class.type = ""
        self.test_class.save()
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        assert_good_sched_event_form_wizard(response, self.test_class)
'''