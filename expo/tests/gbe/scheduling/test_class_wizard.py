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
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe_forms_text import event_type_options
from tests.functions.gbe_scheduling_functions import assert_event_was_picked_in_wizard
from expo.settings import DATE_FORMAT


class TestClassWizard(TestCase):
    '''Tests for the 2nd and 3rd stage in the class wizard view'''
    view_name = 'create_class_wizard'

    def setUp(self):
        self.room = RoomFactory()
        self.teacher = PersonaFactory()
        self.current_conference = ConferenceFactory(accepting_bids=True)
        self.day = ConferenceDayFactory(conference=self.current_conference)
        self.test_class = ClassFactory(b_conference=self.current_conference,
                                       e_conference=self.current_conference,
                                       accepted=3,
                                       teacher=self.teacher,
                                       submitted=True)
        self.url = reverse(
            self.view_name,
            args=[self.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
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
            'accepted': 3,
            'submitted': True,
            'eventitem_id': self.test_class.eventitem_id,
            'type': 'Panel',
            'e_title': 'test title',
            'e_description': 'Description',
            'maximum_enrollment': 10,
            'fee': 0,
            'space_needs': 2,
            'max_volunteer': 0,
            'day': self.day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'form-TOTAL_FORMS': "2",
            'form-INITIAL_FORMS': "1",
            'form-MIN_NUM_FORMS': "0",
            'form-MAX_NUM_FORMS': "1000",
            'form-0-role': 'Teacher',
            'form-0-worker': self.teacher.pk,
            'form-1-role': 'Volunteer',
            'form-1-worker': "",
            'set_class': 'Finish',
        }
        return data

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        assert_event_was_picked_in_wizard(response, "conference")
        self.assertContains(response, str(self.test_class.b_title))
        self.assertContains(response, str(self.test_class.teacher))

    def test_authorized_user_single_conference(self):
        other_class = ClassFactory(accepted=3,
                                   submitted=True)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, str(other_class.b_title))
        self.assertNotContains(response, str(other_class.teacher))

    def test_auth_user_can_pick_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            '<input checked="checked" id="id_accepted_class_0" ' +
            'name="accepted_class" type="radio" value="%d" />' %
            self.test_class.pk)

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        data['accepted_class'] = "boo"
        response = self.client.post(
            self.url,
            data=data)
        self.assertContains(
            response,
            'That choice is not one of the available choices.')

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

    def test_auth_user_load_class(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.filter(eventitem=self.test_class)
        self.assertRedirects(response, "%s?%s-day=%d&filter=Filter&new=%d" % (
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.current_conference.conference_slug]),
            self.current_conference.conference_slug,
            self.day.pk,
            occurrence[0].pk))
