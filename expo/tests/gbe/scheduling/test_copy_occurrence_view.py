from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
)
from scheduler.models import Event
from gbe.models import Class
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from gbe_forms_text import event_type_options
from tests.functions.gbe_scheduling_functions import (
    assert_event_was_picked_in_wizard,
    assert_good_sched_event_form_wizard,
)
from expo.settings import (
    DATE_FORMAT,
    DATETIME_FORMAT,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
    VolunteerContext,
)
from gbe_forms_text import (
    copy_mode_labels,
    copy_mode_choices,
)


class TestClassWizard(TestCase):
    view_name = 'copy_event_schedule'
    copy_date_format = "%a, %b %-d, %Y %-I:%M %p"

    def setUp(self):
        self.context = StaffAreaContext()
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def assert_good_mode_form(self, response, title, date):
        self.assertEqual(response.status_code, 200)
        for day in self.context.days:
            self.assertContains(response, day.day.strftime(DATE_FORMAT))
        self.assertContains(response, copy_mode_choices[0][1])
        self.assertContains(response, copy_mode_choices[1][1])
        self.assertContains(response, "%s - %s" % (
            title,
            date.strftime(DATETIME_FORMAT)))

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Copying - %s: %s" %(
            self.context.area.e_title,
            self.context.sched_event.starttime.strftime(self.copy_date_format)))

    def test_authorized_user_get_no_child_event(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for day in self.context.days:
            self.assertContains(response, day.day.strftime(DATE_FORMAT))
        self.assertNotContains(response, copy_mode_choices[0][1])

    def test_authorized_user_get_w_child_events(self):
        target_event = StaffAreaContext()
        self.context.add_volunteer_opp()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assert_good_mode_form(
            response,
            target_event.area.e_title,
            target_event.sched_event.start_time)

    def test_bad_occurrence(self):
        url = reverse(self.view_name,
            args=[self.context.sched_event.pk+100],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_authorized_user_get_show(self):
        show_context = VolunteerContext()
        target_context = ShowContext()
        url = reverse(self.view_name,
            args=[show_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assert_good_mode_form(
            response,
            target_context.show.e_title,
            target_context.sched_event.start_time)

    def test_authorized_user_get_show(self):
        copy_class = ClassFactory()
        vol_context = VolunteerContext(event=copy_class)
        target_context = ClassContext()
        url = reverse(self.view_name,
            args=[vol_context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assert_good_mode_form(
            response,
            target_context.bid.e_title,
            target_context.sched_event.start_time)

    def test_copy_single_event(self):
        another_day = ConferenceDayFactory(conference=self.context.conference)
        data = {
            'copy_to_day': another_day.pk,
            'pick_mode': "Next",
        }
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data=data, follow=True)
        max_pk = Event.objects.latest('pk').pk
        redirect_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[another_day.conference.conference_slug]),
            another_day.conference.conference_slug,
            another_day.pk,
            str([max_pk]),)
        self.assertRedirects(response, redirect_url)
