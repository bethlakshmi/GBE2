from django.http import Http404
from django import forms
import gbe.models as conf
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from scheduler.views import add_event
from scheduler.forms import conference_days
from scheduler.models import LocationItem
import factories
import mock
import functions


class TestAddEvent(TestCase):
    '''Tests for add_event view'''
    fixtures = ['scheduler/fixtures/rooms.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.eventitem = factories.GenericEventFactory.create()
        self.profile_factory = factories.ProfileFactory
        self.client = Client()
        self.rooms = [factories.RoomFactory.create(),
                      factories.RoomFactory.create(),
                      factories.RoomFactory.create()]

    def get_add_session_form(self):
        return {'event-day': conference_days[1][0],
                'event-time': "12:00:00",
                'event-duration': "1:00:00",
                'event-location': self.rooms[0],
                'event-max_volunteer': 0,
                'title': 'New Title',
                'description': 'New Description',
                }

    @nt.raises(Http404)
    def test_add_event_no_eventitem(self):
        '''Should get 404 if no valid act ID'''
        request = self.factory.get('/scheduler/create/GenericEvent/-1')
        request.user = self.profile_factory.create().user_object
        response = add_event(request, -1)

    @nt.raises(Http404)
    def test_add_event_no_permission(self):
        '''add event attempt should fail because user is not a Schedule Maven
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('/scheduler/create/GenericEvent/%d' %
                                   self.eventitem.pk)
        request.user = profile.user_object
        response = add_event(request, self.eventitem.pk, "GenericEvent")

    def test_add_event_get_succeed(self):
        '''add event get succeeds, user has proper privileges
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('/scheduler/create/GenericEvent/%d' %
                                   self.eventitem.pk)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Scheduling Mavens')
        response = add_event(request, self.eventitem.pk, "GenericEvent")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.eventitem.title in response.content)
        self.assertTrue(self.eventitem.description in response.content)

    def test_add_event_submit_succeed(self):
        '''add event post succeeds, user has proper privileges
        '''
        profile = self.profile_factory.create()
        form_post = self.get_add_session_form()
        request = self.factory.post('/scheduler/create/GenericEvent/%d' %
                                    self.eventitem.pk,
                                    form_post)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Scheduling Mavens')
        '''
        rooms = LocationItem.objects.all().order_by('room__name')
        for loc in rooms:
            print "Room:" + loc.__str__() + "| \n"
        '''
        response = add_event(request, self.eventitem.pk, "GenericEvent")

        self.assertEqual(response.status_code, 200)
        '''
        # BB - when code smell in EventScheduleForm is fixed, these should be
        #print(response.content)
        #self.assertFalse('<font color="red">!</font>' in response.content)
        #self.assertTrue("Events Information" in response.content)
        '''
