import pytest
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from scheduler.views import calendar_view
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
)
from tests.functions.gbe_functions import clear_conferences
from tests.functions.scheduler_functions import noon
from gbe.models import Conference
from datetime import (
    date,
)
from tests.contexts import (
    ClassContext,
    ShowContext
)


class TestCalendarView(TestCase):
    view_name = 'contact_by_role'

    def setUp(self):
        self.client = Client()
        clear_conferences()
        conference = ConferenceFactory()
        conference_day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 02, 06))
        self.showcontext = ShowContext(conference=conference)
        self.other_conference = ConferenceFactory(
            status='completed')
        self.other_conf_day = ConferenceDayFactory(
            conference=self.other_conference,
            day=date(2015, 02, 06))
        self.other_show = ShowContext(conference=self.other_conference)
        self.classcontext = ClassContext(
            conference=self.showcontext.conference,
            starttime=noon(conference_day))

    def test_calendar_view_shows_current_conf_by_default(self):
        url = reverse('calendar_view', urlconf="scheduler.urls")
        response = self.client.get(url)
        self.assertTrue(self.showcontext.show.title in response.content)
        self.assertFalse(self.other_show.show.title in response.content)

    def test_calendar_view_event_shows_all_events(self):
        url = reverse('calendar_view_day',
                      urlconf="scheduler.urls",
                      kwargs={'event_type': 'All',
                              'day': 'Saturday'})
        response = self.client.get(url)
        self.assertContains(response, self.showcontext.show.title)
        self.assertFalse(self.other_show.show.title in response.content)

    def test_calendar_view_shows_requested_conference(self):
        url = reverse('calendar_view', urlconf="scheduler.urls")
        data = {'conf': self.other_conference.conference_slug}
        response = self.client.get(url, data=data)
        self.assertFalse(self.showcontext.show.title in response.content)
        self.assertTrue(self.other_show.show.title in response.content)

    def test_no_conference_days(self):
        clear_conferences()
        ConferenceFactory(status='upcoming')
        url = reverse('calendar_view_day',
                      urlconf='scheduler.urls',
                      kwargs={'event_type': 'Class',
                              'day': 'Sunday'})
        client = Client()
        response = self.client.get(url)
        self.assertNotContains(
            response,
            '<li><a href="http://burlesque-expo.com/class_rooms">')
        self.assertContains(
            response,
            '<p>This calendar is not currently available.</p>')

    def test_no_day(self):
        '''
        There is a day, but that's not the day we're asking for.
        '''
        clear_conferences()
        conference = ConferenceFactory(status='upcoming')
        conference_day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 02, 06))
        url = reverse('calendar_view_day',
                      urlconf='scheduler.urls',
                      kwargs={'event_type': 'Class',
                              'day': 'Sunday'})
        client = Client()
        response = self.client.get(url)
        self.assertNotContains(
            response,
            '<li><a href="http://burlesque-expo.com/class_rooms">')
        self.assertContains(
            response,
            '<p>This calendar is not currently available.</p>')

    def test_no_sched_events(self):
        '''
        There is a day, but that's not the day we're asking for.
        '''
        clear_conferences()
        conference = ConferenceFactory(status='upcoming')
        conference_day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 02, 06))
        url = reverse('calendar_view_day',
                      urlconf='scheduler.urls',
                      kwargs={'event_type': 'Class',
                              'day': 'Saturday'})
        client = Client()
        response = self.client.get(url)
        self.assertNotContains(
            response,
            '<li><a href="http://burlesque-expo.com/class_rooms">')
        self.assertContains(
            response,
            '<p>This calendar is not currently available.</p>')

    def test_calendar_view_class(self):
        sunday = ConferenceDayFactory(
            conference=self.showcontext.conference,
            day=date(2016, 02, 07))
        classcontextSun = ClassContext(
            conference=self.showcontext.conference,
            starttime=noon(sunday))
        url = reverse('calendar_view_day',
                      urlconf="scheduler.urls",
                      kwargs={'event_type': 'Class',
                              'day': 'Saturday'})
        response = self.client.get(url)
        self.assertTrue(self.classcontext.bid.title in response.content)
        self.assertFalse(self.showcontext.show.title in response.content)
        self.assertContains(response, str(self.classcontext.room))
        self.assertNotContains(response, str(classcontextSun.room))

    def test_calendar_view_movement_class(self):
        self.classcontext.bid.type = 'Movement'
        self.classcontext.bid.save()
        url = reverse('calendar_view_day',
                      urlconf="scheduler.urls",
                      kwargs={'event_type': 'Movement',
                              'day': 'Saturday'})
        response = self.client.get(url)
        self.assertTrue(self.classcontext.bid.title in response.content)
        self.assertFalse(self.showcontext.show.title in response.content)
