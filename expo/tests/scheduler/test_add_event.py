from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ClassFactory,
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
    login_as,
)
from tests.contexts import (
    ClassContext,
    PanelContext,
    StaffAreaContext
)
from scheduler.models import Event
import pytz
from datetime import datetime, time


class TestAddEvent(TestCase):
    view_name = 'create_event'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.eventitem = GenericEventFactory()

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id+1])
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 404)

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(self.eventitem.title,
                     response.content)
        nt.assert_in(self.eventitem.description,
                     response.content)
        nt.assert_in('<input id="id_event-duration" name="event-duration" ' +
                     'type="text" value="01:00:00" />',
                     response.content)

    def test_good_user_get_class(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(context.bid.title,
                     response.content)
        nt.assert_in(context.bid.description,
                     response.content)
        nt.assert_in('<input id="id_event-duration" name="event-duration" ' +
                     'type="text" value="01:00:00" />',
                     response.content)

    def test_good_user_minimal_post(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.post(
            url,
            data={'event-day': context.days[0].pk,
                  'event-time': "12:00:00",
                  'event-location': context.room.pk,
                  'event-max_volunteer': 3,
                  'event-title': 'New Title',
                  'event-description': 'New Description',
                  },
            follow=True)

        assert_redirects(response, reverse('event_schedule',
                                           urlconf='scheduler.urls',
                                           args=["Class"]))

        nt.assert_not_in('<ul class="errorlist">', response.content)
        nt.assert_in('Events Information', response.content)
        sessions = Event.objects.filter(eventitem=context.bid, max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()
        nt.assert_equal(session.starttime,
                        datetime.combine(context.days[0].day,
                                         time(12, 0, 0, tzinfo=pytz.utc)))
        nt.assert_in('New Title', response.content)
        nt.assert_in(str(context.room), response.content)
        nt.assert_in('3', response.content)

    def test_good_user_invalid_submit(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.post(
            url,
            data={'event-day': context.days[0].pk,
                  'event-time': "12:00:00",
                  'event-location': 'bad room',
                  'event-max_volunteer': 3,
                  'event-title': 'New Title',
                  'event-description': 'New Description',
                  })

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
        nt.assert_in('<option value="'+str(context.days[0].pk) +
                     '" selected="selected">'+str(context.days[0]) +
                     '</option>',
                     response.content)
        nt.assert_in('<li>Select a valid choice. That choice is not one of ' +
                     'the available choices.</li>',
                     response.content)

    def test_good_user_with_duration(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.post(
            url,
            data={'event-day': context.days[0].pk,
                  'event-time': "12:00:00",
                  'event-location': context.room.pk,
                  'event-duration': "3:00:00",
                  'event-max_volunteer': 3,
                  'event-title': 'New Title',
                  'event-description': 'New Description',
                  },
            follow=True)

        assert_redirects(response, reverse('event_schedule',
                                           urlconf='scheduler.urls',
                                           args=["Class"]))
        nt.assert_in('Events Information', response.content)
        nt.assert_in("3:00",
                     response.content)

    def test_good_user_with_teacher(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = ClassContext()
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.post(
            url,
            data={'event-day': context.days[0].pk,
                  'event-time': "12:00:00",
                  'event-location': context.room.pk,
                  'event-max_volunteer': 3,
                  'event-title': 'New Title',
                  'event-description': 'New Description',
                  'event-teacher': overcommitter.pk,
                  },
            follow=True)

        assert_redirects(response, reverse('event_schedule',
                                           urlconf='scheduler.urls',
                                           args=["Class"]))
        nt.assert_in('Events Information', response.content)
        sessions = Event.objects.filter(eventitem=context.bid, max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()
        teachers = session.get_direct_workers('Teacher')
        nt.assert_equal(len(teachers), 1)
        nt.assert_equal(teachers[0].pk, overcommitter.pk)

    def test_good_user_with_moderator(self):
        Conference.objects.all().delete()
        Room.objects.all().delete()
        context = PanelContext()
        overcommitter = PersonaFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", context.bid.eventitem_id])
        response = self.client.post(
            url,
            data={'event-day': context.days[0].pk,
                  'event-time': "12:00:00",
                  'event-location': context.room.pk,
                  'event-max_volunteer': 3,
                  'event-title': 'New Title',
                  'event-description': 'New Description',
                  'event-moderator': overcommitter.pk,
                  },
            follow=True)

        assert_redirects(response, reverse('event_schedule',
                                           urlconf='scheduler.urls',
                                           args=["Class"]))
        nt.assert_in('Events Information', response.content)
        sessions = Event.objects.filter(eventitem=context.bid, max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()
        moderators = session.get_direct_workers('Moderator')
        nt.assert_equal(len(moderators), 1)
        nt.assert_equal(moderators[0].pk, overcommitter.pk)

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
                            context.sched_event.eventitem.eventitem_id])
        response = self.client.post(
            url,
            data={'event-day': context.days[0].pk,
                  'event-time': "12:00:00",
                  'event-location': room.pk,
                  'event-max_volunteer': 3,
                  'event-title': 'New Title',
                  'event-description': 'New Description',
                  'event-staff_lead': overcommitter.pk,
                  },
            follow=True)
        assert_redirects(response, reverse('event_schedule',
                                           urlconf='scheduler.urls',
                                           args=["GenericEvent"]))
        nt.assert_in('Events Information', response.content)
        sessions = Event.objects.filter(
            eventitem=context.sched_event.eventitem,
            max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()

        leads = Worker.objects.filter(role="Staff Lead",
                                      allocations__event=session)
        nt.assert_equal(len(leads), 1)
        nt.assert_equal(leads.first().workeritem.pk, overcommitter.pk)

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
                      args=["Class", context.bid.eventitem_id])
        response = self.client.post(
            url,
            data={'event-day': context.days[0].pk,
                  'event-time': "12:00:00",
                  'event-location': context.room.pk,
                  'event-max_volunteer': 3,
                  'event-title': 'New Title',
                  'event-description': 'New Description',
                  'event-panelists': [overcommitter1.pk, overcommitter2.pk]
                  },
            follow=True)

        assert_redirects(response, reverse('event_schedule',
                                           urlconf='scheduler.urls',
                                           args=["Class"]))
        nt.assert_in('Events Information', response.content)
        sessions = Event.objects.filter(eventitem=context.bid, max_volunteer=3)
        nt.assert_equal(len(sessions), 1)
        session = sessions.first()
        leads = session.get_direct_workers('Panelist')
        nt.assert_equal(len(leads), 2)
        nt.assert_in(leads[0].pk, [overcommitter1.pk, overcommitter2.pk])
        nt.assert_in(leads[1].pk, [overcommitter1.pk, overcommitter2.pk])
