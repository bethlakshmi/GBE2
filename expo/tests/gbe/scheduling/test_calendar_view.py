import pytest
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
)
from tests.functions.gbe_functions import clear_conferences
from tests.functions.scheduler_functions import noon
from datetime import (
    date,
    datetime,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
)


class TestCalendarView(TestCase):
    view_name = 'contact_by_role'

    def setUp(self):
        self.client = Client()
        clear_conferences()
        conference = ConferenceFactory()
        save_the_date = datetime(2016, 02, 06, 12, 00, 00)
        self.staffcontext = StaffAreaContext(
            conference=conference,
            starttime=save_the_date)
        self.showcontext = ShowContext(conference=conference,
                                       starttime=save_the_date)
        self.other_conference = ConferenceFactory(
            status='completed')
        self.other_conf_day = ConferenceDayFactory(
            conference=self.other_conference,
            day=date(2015, 02, 06))
        self.other_show = ShowContext(conference=self.other_conference)
        self.classcontext = ClassContext(
            conference=conference,
            starttime=save_the_date)
        self.volunteeropp = self.staffcontext.add_volunteer_opp()

    def test_calendar_generic_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % self.showcontext.conference.conference_name)
        self.assertContains(response, self.showcontext.show.e_title)
        self.assertNotContains(response, self.other_show.show.e_title)
        self.assertNotContains(response, self.classcontext.bid.e_title)
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)

    def test_calendar_conference_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Conference'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % self.showcontext.conference.conference_name)
        self.assertNotContains(response, self.showcontext.show.e_title)
        self.assertNotContains(response, self.other_show.show.e_title)
        self.assertContains(response, self.classcontext.bid.e_title)
        self.assertNotContains(response, self.volunteeropp.eventitem.e_title)

    def test_calendar_volunteer_w_default_conf(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['Volunteer'])
        response = self.client.get(url)
        self.assertContains(
            response,
            '<div class="col-lg-12">%s' % self.showcontext.conference.conference_name)
        self.assertNotContains(response, self.showcontext.show.e_title)
        self.assertNotContains(response, self.other_show.show.e_title)
        self.assertNotContains(response, self.classcontext.bid.e_title)
        self.assertContains(response, self.volunteeropp.eventitem.e_title)

    def test_calendar_shows_requested_conference(self):
        url = reverse('calendar',
                      urlconf="gbe.scheduling.urls",
                      args=['General'])
        data = {'conference': self.other_conference.conference_slug}
        response = self.client.get(url, data=data)
        self.assertNotContains(response, self.showcontext.show.e_title)
        self.assertContains(response, self.other_show.show.e_title)

    def test_no_conference_days(self):
        clear_conferences()
        ConferenceFactory(status='upcoming')
        url = reverse('calendar',
                      urlconf='gbe.scheduling.urls',
                      args=['Conference'])
        response = self.client.get(url)
        self.assertContains(
            response,
            'This calendar is not currently available.')
'''

    def test_no_day(self):
        '''
#        There is a day, but that's not the day we're asking for.
'''
        clear_conferences()
        conference = ConferenceFactory(status='upcoming')
        conference_day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 02, 06))
        url = reverse('calendar_day',
                      urlconf='gbe.scheduling.urls',
                      kwargs={'event_type': 'Class',
                              'day': 'Sunday'})
        response = self.client.get(url)
        self.assertNotContains(
            response,
            '<li><a href="http://burlesque-expo.com/class_rooms">')
        self.assertContains(
            response,
            '<p>This calendar is not currently available.</p>')

    def test_no_sched_events(self):
        '''
'''        There is a day, but that's not the day we're asking for.
        clear_conferences()
        conference = ConferenceFactory(status='upcoming')
        conference_day = ConferenceDayFactory(
            conference=conference,
            day=date(2016, 02, 06))
        url = reverse('calendar_day',
                      urlconf='gbe.scheduling.urls',
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

    def test_calendar_class(self):
        sunday = ConferenceDayFactory(
            conference=self.showcontext.conference,
            day=date(2016, 02, 07))
        classcontextSun = ClassContext(
            conference=self.showcontext.conference,
            starttime=noon(sunday))
        url = reverse('calendar_day',
                      urlconf="gbe.scheduling.urls",
                      kwargs={'event_type': 'Class',
                              'day': 'Saturday'})
        response = self.client.get(url)
        self.assertTrue(self.classcontext.bid.e_title in response.content)
        self.assertFalse(self.showcontext.show.e_title in response.content)
        self.assertContains(response, str(self.classcontext.room))
        self.assertNotContains(response, str(classcontextSun.room))

    def test_calendar_movement_class(self):
        self.classcontext.bid.type = 'Movement'
        self.classcontext.bid.save()
        url = reverse('calendar_day',
                      urlconf="gbe.scheduling.urls",
                      kwargs={'event_type': 'Movement',
                              'day': 'Saturday'})
        response = self.client.get(url)
        self.assertTrue(self.classcontext.bid.e_title in response.content)
        self.assertFalse(self.showcontext.show.e_title in response.content)
'''