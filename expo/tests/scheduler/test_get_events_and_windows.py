import nose.tools as nt
import pytz
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from scheduler.functions import get_events_and_windows
from datetime import datetime
from tests.factories.gbe_factories import (
    ConferenceFactory,
    VolunteerWindowFactory
)
from gbe.models import GenericEvent
from scheduler.models import Event as sEvent
import mock


class TestGetEventsAndWindows(TestCase):
    '''Tests for get_events_and_windows function'''
    def setUp(self):
        self.window = VolunteerWindowFactory.create()
        self.volunteer_event = GenericEvent()
        self.volunteer_event.e_conference = self.window.day.conference
        self.volunteer_event.save()
        self.s_event = sEvent()
        self.s_event.eventitem = self.volunteer_event
        self.s_event.starttime = datetime(2016, 2, 5, 12, 0, 0, 0, pytz.utc)
        self.s_event.max_volunteer = 10
        self.s_event.save()

    def test_get_one_event_and_window(self):
        '''should get 1 event, and 1 window
        '''
        results = get_events_and_windows(self.window.day.conference)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['event'].pk, self.s_event.pk)
        self.assertEqual(results[0]['window'].pk, self.window.pk)

    def test_empty_conference(self):
        '''should get no events, and no windows
        '''
        conference = ConferenceFactory.create()
        results = get_events_and_windows(conference)
        self.assertEqual(len(results), 0)

    def test_get_two_events_and_window(self):
        '''should get 2 events, each within the same window
        '''
        s_event2 = sEvent()
        s_event2.eventitem = self.volunteer_event
        s_event2.starttime = datetime(2016, 2, 5, 10, 0, 0, 0, pytz.utc)
        s_event2.max_volunteer = 10
        s_event2.save()

        results = get_events_and_windows(self.window.day.conference)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['event'].pk, s_event2.pk)
        self.assertEqual(results[0]['window'].pk, self.window.pk)
        self.assertEqual(results[1]['event'].pk, self.s_event.pk)
        self.assertEqual(results[1]['window'].pk, self.window.pk)
