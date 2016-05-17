from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
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
from scheduler.models import Event
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

    def get_edit_event_form(self, context, room=None):
        room = room or context.room
        form_dict = {'event-day': context.days[0].pk,
                     'event-time': "12:00:00",
                     'event-location': room.pk,
                     'event-max_volunteer': 3,
                     'event-title': 'New Title',
                     'event-description': 'New Description',
                     }
        return form_dict

    def assert_good_get(self, response, eventitem):
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(eventitem.title,
                     response.content)
        nt.assert_in(eventitem.description,
                     response.content)
        nt.assert_in('<input id="id_event-duration" name="event-duration" ' +
                     'type="text" value="01:00:00" />',
                     response.content)

    def assert_good_post(self,
                         response,
                         context,
                         day,
                         room,
                         event_type="Class"):
        assert_redirects(response, reverse(self.view_name,
                                           urlconf="scheduler.urls",
                                           args=[event_type, context.sched_event.pk]))

        nt.assert_not_in('<ul class="errorlist">', response.content)
        # check title
        nt.assert_in('<H1 class="sched_detail_title">New Title</H1>',
                     response.content)
        # check day
        nt.assert_in('<option value="' +
                     str(day.pk) +
                     '" selected="selected">',
                     response.content)
        # check time
        nt.assert_in('<option value="12:00:00" selected="selected">',
                     response.content)
        # check location
        nt.assert_in('<option value="' +
                     str(room.pk) +
                     '" selected="selected">' +
                     str(room),
                     response.content)
        # check volunteers
        nt.assert_in('<input id="id_event-max_volunteer" min="0" ' +
                     'name="event-max_volunteer" type="number" value="3" />',
                     response.content)
        # check description
        nt.assert_in('New Description', response.content)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        assert_redirects(response, redirect_url)
        nt.assert_true(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk+1])
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 404)

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        response = self.client.get(url)
        self.assert_good_get(response, self.context.bid)

    def test_good_user_minimal_post(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = self.get_edit_event_form(self.context)
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
        form_data = self.get_edit_event_form(self.context)
        form_data['event-location'] = 'bad room'
        response = self.client.post(
            url,
            data=form_data)

        nt.assert_equal(response.status_code, 200)
        nt.assert_in('<input id="id_event-title" name="event-title" ' +
                     'type="text" value="New Title" />',
                     response.content)
        nt.assert_in("New Description",
                     response.content)
        nt.assert_in('<input id="id_event-max_volunteer" min="0" ' +
                     'name="event-max_volunteer" type="number" value="3" />',
                     response.content)
        nt.assert_in('<option value="12:00:00" selected="selected">' +
                     '12:00 PM</option>',
                     response.content)
        nt.assert_in('<option value="'+str(self.context.days[0].pk) +
                     '" selected="selected">'+str(self.context.days[0]) +
                     '</option>',
                     response.content)
        nt.assert_in('<li>Select a valid choice. That choice is not one of ' +
                     'the available choices.</li>',
                     response.content)

    def test_good_user_with_duration(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = self.get_edit_event_form(self.context)
        form_data['event-duration'] = "3:00:00"
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              self.context,
                              self.context.days[0],
                              self.context.room)
        nt.assert_in('<input id="id_event-duration" name="event-duration" ' +
                     'type="text" value="03:00:00" />',
                     response.content)

    def test_good_user_with_teacher(self):
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", self.context.sched_event.pk])
        form_data = self.get_edit_event_form(self.context)
        form_data['event-teacher'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)
 
        self.assert_good_post(response,
                              self.context,
                              self.context.days[0],
                              self.context.room)
        sessions = Event.objects.filter(eventitem=self.context.bid,
                                        max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()
        teachers = session.get_direct_workers('Teacher')
        nt.assert_equal(len(teachers), 1)
        nt.assert_equal(teachers[0].pk, overcommitter.pk)
        nt.assert_in('<option value="' + str(overcommitter.pk) +
                     '" selected="selected">' + str(overcommitter) +
                     '</option>',
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
        form_data = self.get_edit_event_form(context)
        form_data['event-moderator'] = overcommitter.pk
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              context,
                              context.days[0],
                              context.room)
        sessions = Event.objects.filter(eventitem=context.bid, max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()
        moderators = session.get_direct_workers('Moderator')
        nt.assert_equal(len(moderators), 1)
        nt.assert_equal(moderators[0].pk, overcommitter.pk)
        nt.assert_in('<option value="' + str(overcommitter.pk) +
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
        form_data = self.get_edit_event_form(context, room=room)
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
        sessions = Event.objects.filter(
            eventitem=context.sched_event.eventitem,
            max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()

        leads = Worker.objects.filter(role="Staff Lead",
                                      allocations__event=session)
        nt.assert_equal(len(leads), 1)
        nt.assert_equal(leads.first().workeritem.pk, overcommitter.pk)
        nt.assert_in('<option value="' + str(overcommitter.pk) +
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
        form_data = self.get_edit_event_form(context)
        form_data['event-panelists'] = [overcommitter1.pk, overcommitter2.pk]
        response = self.client.post(
            url,
            data=form_data,
            follow=True)

        self.assert_good_post(response,
                              context,
                              context.days[0],
                              context.room)
        sessions = Event.objects.filter(eventitem=context.bid, max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()
        leads = session.get_direct_workers('Panelist')
        nt.assert_equal(len(leads), 2)
        nt.assert_in(leads[0].pk, [overcommitter1.pk, overcommitter2.pk])
        nt.assert_in(leads[1].pk, [overcommitter1.pk, overcommitter2.pk])
        nt.assert_in('<option value="' + str(overcommitter1.pk) +
                     '" selected="selected">' + str(overcommitter1) +
                     '</option>',
                     response.content)
        nt.assert_in('<option value="' + str(overcommitter2.pk) +
                     '" selected="selected">' + str(overcommitter2) +
                     '</option>',
                     response.content)
