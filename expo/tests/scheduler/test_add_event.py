from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ClassFactory,
    GenericEventFactory,
    ProfileFactory,
)
from gbe.models import (
    Conference,
    ConferenceDay,
    Room
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    ClassContext,
)

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
        nt.assert_in(str(self.eventitem.duration),
                     response.content)

    def test_good_user_get_class(self):
        login_as(self.privileged_profile, self)
        klass = ClassFactory()
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", klass.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(klass.title,
                     response.content)
        nt.assert_in(klass.description,
                     response.content)
        nt.assert_in("1:00",
                     response.content)
        nt.assert_in(str(klass.teacher),
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
                  })

        print(response.content)

        assert_redirects(response, reverse('event_schedule',
                                           urlconf='scheduler.urls',
                                           args=["Class"]))
        nt.assert_in('<input id="id_event-title" name="event-title" '+
                     'type="text" value="New Title" />',
                     response.content)
        nt.assert_in("New Description",
                     response.content)
        nt.assert_in('<input id="id_event-max_volunteer" min="0" '+
                     'name="event-max_volunteer" type="number" value="3" />',
                     response.content)
        nt.assert_in('<option value="12:00:00" selected="selected">'+
                     '12:00 PM</option>',
                     response.content)
        nt.assert_in('<option value="'+str(context.days[0].pk)+
                     '" selected="selected">'+str(context.days[0])+'</option>',
                     response.content)
        nt.assert_not_in('<ul class="errorlist">', response.content)

    def test_good_user_invalid_submit(self):
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", context.bid.eventitem_id])
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
        nt.assert_in("New Description",
                     response.content)
        nt.assert_in('<li>Select a valid choice. That choice is not one of '+
                     'the available choices.</li>',
                     response.content)

'''
    def test_good_user_with_time(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        overcommitter = PersonaFactory()
        response = self.client.post(
            url,
            data={'event-day': self.day.pk,
                'event-time': "12:00:00",
                'event-duration': "1:00:00",
                'event-location': self.room,
                'event-max_volunteer': 0,
                'title': 'New Title',
                'description': 'New Description',
                })
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(self.eventitem.title,
                     response.content)
        nt.assert_in(self.eventitem.description,
                     response.content)
        nt.assert_in(str(self.eventitem.duration),
                     response.content)

    def test_good_user_with_teacher(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        overcommitter = PersonaFactory()
        response = self.client.post(
            url,
            data={'event-day': self.day.pk,
                'event-time': "12:00:00",
                'event-duration': "1:00:00",
                'event-location': self.room,
                'event-max_volunteer': 0,
                'title': 'New Title',
                'description': 'New Description',
                'teacher': overcommiter.pk,
                })
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(self.eventitem.title,
                     response.content)
        nt.assert_in(self.eventitem.description,
                     response.content)
        nt.assert_in(str(self.eventitem.duration),
                     response.content)

    def test_good_user_with_moderator(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        overcommitter = PersonaFactory()
        response = self.client.post(
            url,
            data={'event-day': self.day.pk,
                'event-time': "12:00:00",
                'event-duration': "1:00:00",
                'event-location': self.room,
                'event-max_volunteer': 0,
                'title': 'New Title',
                'description': 'New Description',
                'moderator': overcommiter.pk,
                })
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(self.eventitem.title,
                     response.content)
        nt.assert_in(self.eventitem.description,
                     response.content)
        nt.assert_in(str(self.eventitem.duration),
                     response.content)
'''
