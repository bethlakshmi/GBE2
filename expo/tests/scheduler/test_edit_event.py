from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceDayFactory,
    GenericEventFactory,
    ProfileFactory,
    PersonaFactory,
    RoomFactory
)
from gbe.models import (
    Conference,
    Room
)
from scheduler.models import Worker
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import (
    ClassContext,
    PanelContext,
    StaffAreaContext
)
from tests.functions.scheduler_functions import (
    assert_good_sched_event_form,
    get_sched_event_form
)
import pytz
from datetime import (
    date,
    time,
    timedelta,
)


class TestEditEvent(TestCase):
    view_name = 'edit_event'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        Conference.objects.all().delete()
        Room.objects.all().delete()
        self.context = ClassContext()

    def assert_good_post(self,
                         response,
                         context,
                         day,
                         room,
                         event_type="Class"):
        self.assertRedirects(response, reverse(
            self.view_name,
            urlconf="scheduler.urls",
            args=[event_type, context.sched_event.pk]))

        self.assertNotIn('<ul class="errorlist">', response.content)
        # check title
        self.assertIn('<H1 class="sched_detail_title">New Title</H1>',
                      response.content)
        # check day
        self.assertIn('<option value="' +
                      str(day.pk) +
                      '" selected="selected">',
                      response.content)
        # check time
        self.assertIn('<option value="12:00:00" selected="selected">',
                      response.content)
        # check location
        self.assertIn('<option value="' +
                      str(room.pk) +
                      '" selected="selected">' +
                      str(room),
                      response.content)
        # check volunteers
        self.assertIn('<input id="id_event-max_volunteer" min="0" ' +
                      'name="event-max_volunteer" type="number" value="3" />',
                      response.content)
        # check description
        self.assertIn('New Description', response.content)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk+1])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        response = self.client.get(url)
        assert_good_sched_event_form(response, self.context.bid)

    def test_good_user_minimal_post(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = get_sched_event_form(self.context)
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        self.assert_good_post(response,
                              self.context,
                              self.context.days[0],
                              self.context.room)

    def test_good_user_invalid_submit(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = get_sched_event_form(self.context)
        form_data['event-location'] = 'bad room'
        response = self.client.post(
            url,
            data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<input id="id_event-title" name="event-title" ' +
                      'type="text" value="New Title" />',
                      response.content)
        self.assertIn("New Description",
                      response.content)
        self.assertIn('<input id="id_event-max_volunteer" min="0" ' +
                      'name="event-max_volunteer" type="number" value="3" />',
                      response.content)
        self.assertIn('<option value="12:00:00" selected="selected">',
                      response.content)
        self.assertIn('<option value="'+str(self.context.days[0].pk) +
                      '" selected="selected">'+str(self.context.days[0]) +
                      '</option>',
                      response.content)
        self.assertIn('<li>Select a valid choice. That choice is not one of ' +
                      'the available choices.</li>',
                      response.content)

    def test_good_user_with_duration(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = get_sched_event_form(self.context)
        form_data['event-duration'] = "3:00:00"
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              self.context,
                              self.context.days[0],
                              self.context.room)
        self.assertIn('<input id="id_event-duration" name="event-duration" ' +
                      'type="text" value="03:00:00" />',
                      response.content)

    def test_no_duration(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = get_sched_event_form(self.context)
        del form_data['event-duration']
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        self.assertIn("This field is required.",
                      response.content)

    def test_good_user_change_room(self):
        login_as(self.privileged_profile, self)
        new_room = RoomFactory()
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = get_sched_event_form(self.context, new_room)
        form_data['event-duration'] = "3:00:00"
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              self.context,
                              self.context.days[0],
                              new_room)

    def test_good_user_with_teacher(self):
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = get_sched_event_form(self.context)
        form_data['event-teacher'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              self.context,
                              self.context.days[0],
                              self.context.room)
        teachers = self.context.sched_event.get_direct_workers('Teacher')
        self.assertEqual(len(teachers), 1)
        self.assertEqual(teachers[0].pk, overcommitter.pk)
        self.assertIn('<option value="' + str(overcommitter.pk) +
                      '" selected="selected">' + str(overcommitter) +
                      '</option>',
                      response.content)

    def test_good_user_remove_teacher(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = get_sched_event_form(self.context)
        form_data['event-teacher'] = ""
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              self.context,
                              self.context.days[0],
                              self.context.room)
        teachers = self.context.sched_event.get_direct_workers('Teacher')
        self.assertEqual(len(teachers), 0)
        self.assertIn(
            '<select id="id_event-teacher" name="event-teacher">\n' +
            '<option value="" selected="selected">---------</option>',
            response.content)

    def test_good_user_with_moderator(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = PanelContext()
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.sched_event.pk])
        form_data = get_sched_event_form(context)
        form_data['event-moderator'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              context,
                              context.days[0],
                              context.room)
        moderators = context.sched_event.get_direct_workers('Moderator')
        self.assertEqual(len(moderators), 1)
        self.assertEqual(moderators[0].pk, overcommitter.pk)
        self.assertIn('<option value="' + str(overcommitter.pk) +
                      '" selected="selected">' + str(overcommitter) +
                      '</option>',
                      response.content)

    def test_good_user_with_staff_area_lead(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        room = RoomFactory()
        context = StaffAreaContext()
        overcommitter = ProfileFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent",
                            context.sched_event.pk])
        form_data = get_sched_event_form(context, room=room)
        form_data['event-staff_lead'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
        self.assert_good_post(response,
                              context,
                              context.days[0],
                              room,
                              "GenericEvent")
        leads = Worker.objects.filter(
            role="Staff Lead",
            allocations__event=context.sched_event)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads.first().workeritem.pk, overcommitter.pk)
        self.assertIn('<option value="' + str(overcommitter.pk) +
                      '" selected="selected">' + str(overcommitter) +
                      '</option>',
                      response.content)

    def test_good_user_with_panelists(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = PanelContext()
        context.add_panelist()
        overcommitter1 = PersonaFactory()
        overcommitter2 = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.sched_event.pk])
        form_data = get_sched_event_form(context)
        form_data['event-panelists'] = [overcommitter1.pk, overcommitter2.pk]
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              context,
                              context.days[0],
                              context.room)
        leads = context.sched_event.get_direct_workers('Panelist')
        self.assertEqual(len(leads), 2)
        self.assertIn(leads[0].pk, [overcommitter1.pk, overcommitter2.pk])
        self.assertIn(leads[1].pk, [overcommitter1.pk, overcommitter2.pk])
        self.assertIn('<option value="' + str(overcommitter1.pk) +
                      '" selected="selected">' + str(overcommitter1) +
                      '</option>',
                      response.content)
        self.assertIn('<option value="' + str(overcommitter2.pk) +
                      '" selected="selected">' + str(overcommitter2) +
                      '</option>',
                      response.content)
