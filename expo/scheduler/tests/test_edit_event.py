from django.http import Http404
from django import forms
import gbe.models as conf
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from scheduler.views import edit_event
from scheduler.forms import conference_days
from gbe.models import Room
import factories
import mock
import functions


class TestEditEvent(TestCase):
    '''Tests for edit_event view'''
    
    # Fixture to create some rooms, location items, and resource items
    fixtures = ['scheduler/fixtures/rooms.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.s_event = factories.SchedEventFactory.create()
        self.profile_factory = factories.ProfileFactory
        self.client = Client()
        self.room = Room.objects.all().order_by('name').first()
        self.s_event.set_location(self.room)
        
    def get_edit_event_form(self):
        return {'event-day': conference_days[1][0],
                'event-time': "12:00:00",
                'event-duration': "1:00:00",
                'event-location': self.s_event.location,
                'event-max_volunteer': 0,
                'title': 'New Title',
                'description': 'New Description',
                }

    
    @nt.raises(Http404)
    def test_edit_event_no_eventitem(self):
        '''Should get 404 if no valid act ID'''
        request = self.factory.get('/scheduler/create/GenericEvent/-1')
        request.user = self.profile_factory.create().user_object
        response = edit_event(request, -1)

    @nt.raises(Http404)
    def test_edit_event_no_permission(self):
        '''edit event attempt should fail because user is not a Schedule Maven
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('/scheduler/create/GenericEvent/%d' %
                                   self.s_event.pk)
        request.user = profile.user_object
        response = edit_event(request, self.s_event.pk, "GenericEvent")

    def test_edit_event_get_succeed(self):
        '''edit event get succeeds, user has proper privileges
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('/scheduler/create/GenericEvent/%d' %
                                   self.s_event.pk)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Scheduling Mavens')
        response = edit_event(request, self.s_event.pk, "GenericEvent")    
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.s_event.eventitem.title in response.content)
        self.assertTrue(self.s_event.eventitem.description in response.content)
        
    def test_edit_event_submit_succeed(self):
        '''edit event post succeeds without errors
        '''
        profile = self.profile_factory.create()
        form_post = self.get_edit_event_form()
        request = self.factory.post('/scheduler/create/GenericEvent/%d' %
                                   self.s_event.pk,
                                   form_post)
        request.user = profile.user_object
        functions.grant_privilege(profile, 'Scheduling Mavens')
        rooms = Room.objects.all().order_by('name')
        for loc in rooms:
            print "Room:" + loc.__str__() + "| \n"
        response = edit_event(request, self.s_event.pk, "GenericEvent")
        
        self.assertEqual(response.status_code, 200)
        print(response.content)
        self.assertFalse('<font color="red">!</font>' in response.content)
        self.assertTrue(form_post['title'] in response.content)
        self.assertTrue(form_post['description'] in response.content)
