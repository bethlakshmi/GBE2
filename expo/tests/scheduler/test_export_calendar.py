from django.utils import timezone
from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    ConferenceFactory,
    ShowFactory,
    RoomFactory,
    ClassFactory,
)
from tests.factories.scheduler_factories import (
    LocationFactory,
    WorkerFactory,
    SchedEventFactory,
    EventContainerFactory,
    ResourceAllocationFactory,
)
from gbe.models import (
    Conference,
    Room,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import (
    ShowContext,
    ClassContext,
)

from tests.functions.scheduler_functions import (
    assert_good_sched_event_form,
    assert_selected,
    get_sched_event_form,
)
import pytz
from datetime import (
    datetime,
    time,
)
import scheduler.models as sched_event

common_events = (('show', datetime(2016, 02, 5)),
                 ('class', datetime(2016, 02, 5)),
                 ('show', datetime(2016, 02, 6)),
                 ('class', datetime(2016, 02, 6)),
                 ('show', datetime(2016, 02, 7)),
                 ('class', datetime(2016, 02, 7)),
                )                             


class TestExportCalendar(TestCase):
    view_name = 'export_calendar'

    def setUp(self):
        self.client = Client()
        self.conference = ConferenceFactory()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.show = ShowFactory()
        self.classes = ClassFactory()
        self.url = reverse(self.view_name,
                           urlconf="scheduler.urls")
        self.showcontext = ShowContext(conference=self.conference)
        self.classcontext = ClassContext(conference=self.conference)

    def test_no_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_schedule(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertTrue(response.content.count('\n') == 1)
        self.assertTrue('Session Title' in response.content)

    def test_schedule(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        conf = Conference.current_conf()
        show = ShowFactory(conference=conf)
        classes = ClassFactory(conference=conf)
        for event in common_events:
            if event[0] == 'show':
                sched_event = SchedEventFactory(eventitem=show.eventitem_ptr,
                                         starttime= timezone.make_aware(
                                             event[1],
                                             timezone.get_current_timezone()))
            elif event[0] == 'class':
                sched_event = SchedEventFactory(
                    eventitem=classes.eventitem_ptr\,
                    starttime=timezone.make_aware(event[1], timezone \
                                                  .get_current_timezone()))
            sched_event.save()
        login_as(ProfileFactory(), self)

        response = self.client.get(self.url)
        self.assertTrue(response.content.count('\n') > 1)
        self.assertTrue(len(
            (response.content.split('\r\n')[1].split('","'))) >= 8)
        self.assertTrue('Test Show' in
                        response.content.split('\r\n')[1].split('","')[0])

    def test_guidebook(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        conf = Conference.current_conf()
        show = ShowFactory(conference=conf)
        classes = ClassFactory(conference=conf)
        for event in common_events:
            if event[0] == 'show':
                sched_event = SchedEventFactory(eventitem=show.eventitem_ptr,
                                         starttime= timezone.make_aware(
                                             event[1],
                                             timezone.get_current_timezone()))
            elif event[0] == 'class':
                sched_event = SchedEventFactory(
                    eventitem=classes.eventitem_ptr\,
                    starttime=timezone.make_aware(event[1], timezone \
                                                  .get_current_timezone()))
            sched_event.save()
        login_as(ProfileFactory(), self)

        response = self.client.get(self.url)
        self.assertTrue('Test Show' in
                        response.content.split('\r\n')[1].split('","')[0]
                        or 'Test Show' in
                        response.content.split('\r\n')[2].split('","')[0])
        self.assertTrue('Class Title' in
                        response.content.split('\r\n')[1].split('","')[0]
                        or 'Class Title' in
                        response.content.split('\r\n')[2].split('","')[0])

    def test_ical(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        conf = Conference.current_conf()
        show = ShowFactory(conference=conf)
        classes = ClassFactory(conference=conf)
        for event in common_events:
            if event[0] == 'show':
                sched_event = SchedEventFactory(eventitem=show.eventitem_ptr,
                                         starttime= timezone.make_aware(
                                             event[1],
                                             timezone.get_current_timezone()))
            elif event[0] == 'class':
                sched_event = SchedEventFactory(
                    eventitem=classes.eventitem_ptr\,
                    starttime=timezone.make_aware(event[1], timezone \
                                                  .get_current_timezone()))
            sched_event.save()
        login_as(ProfileFactory(), self)

        response = self.client.get(self.url + '?cal_format=ical')
        self.assertTrue('BEGIN:VCALENDAR' in
                        response.content.split('\r\n')[0])
        vevent_count = 0
        for line in response.content.split('\r\n'):
            if 'BEGIN:VEVENT' in line:
                vevent_count = vevent_count + 1
        self.assertTrue(vevent_count > 0)

    '''
    def test_day_all(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        conf = Conference.current_conf()
        show = ShowFactory(conference=conf)
        classes = ClassFactory(conference=conf)
        for event in common_events:
            if event[0] == 'show':
                sched_event = SchedEventFactory(eventitem=show.eventitem_ptr,
                                         starttime= timezone.make_aware(
                                             event[1],
                                             timezone.get_current_timezone()))
            elif event[0] == 'class':
                sched_event = SchedEventFactory(
                    eventitem=classes.eventitem_ptr\,
                    starttime=timezone.make_aware(event[1], timezone \
                                                  .get_current_timezone()))
            sched_event.save()
        login_as(ProfileFactory(), self)

        response = self.client.get(self.url)
        print response
        fri_count, sat_count, sun_count = 0, 0, 0
        for line in response.content.split('\r\n'):
            if 'Feb. 5' in line:
                fri_count = fri_count + 1
            elif 'Feb. 6' in line:
                sat_count = sat_count + 1
            elif 'Feb. 7' in line:
                sun_count = sun_count + 1
        print fri_count, sat_count, sun_count
        self.assertTrue(fri_count == 2 and sat_count == 2 and sun_count == 2)

    def test_day_sat(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        conf = Conference.current_conf()
        show = ShowFactory(conference=conf)
        classes = ClassFactory(conference=conf)
        for event in common_events:
            if event[0] == 'show':
                sched_event = SchedEventFactory(eventitem=show.eventitem_ptr,
                                         starttime= timezone.make_aware(
                                             event[1],
                                             timezone.get_current_timezone()))
            elif event[0] == 'class':
                sched_event = SchedEventFactory(
                    eventitem=classes.eventitem_ptr\,
                    starttime=timezone.make_aware(event[1], timezone \
                                                  .get_current_timezone()))
            sched_event.save()
        login_as(ProfileFactory(), self)

        response = self.client.get(self.url + '?day=Saturday')
        fri_count, sat_count, sun_count = 0, 0, 0
        for line in response.content.split('\r\n'):
            if 'Feb. 6' in line:
                fri_count = fri_count + 1
            elif 'Feb. 7' in line:
                sat_count = sat_count + 1
            elif 'Feb. 8' in line:
                sun_count = sun_count + 1
        self.assertTrue(fri_count == 0 and sat_count == 2 and sun_count == 0)
    '''

    def test_type_class(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        conf = Conference.current_conf()
        show = ShowFactory(conference=conf)
        classes = ClassFactory(conference=conf)
        for event in common_events:
            if event[0] == 'show':
                sched_event = SchedEventFactory(eventitem=show.eventitem_ptr,
                                         starttime= timezone.make_aware(
                                             event[1],
                                             timezone.get_current_timezone()))
            elif event[0] == 'class':
                sched_event = SchedEventFactory(
                    eventitem=classes.eventitem_ptr\,
                    starttime=timezone.make_aware(event[1], timezone \
                                                  .get_current_timezone()))
            sched_event.save()
        login_as(ProfileFactory(), self)

        response = self.client.get(self.url + '?event_types=Class')
        self.assertFalse('Test Show' in
                         response.content.split('\r\n')[1].split('","')[0]
                         or 'Test Show' in
                         response.content.split('\r\n')[2].split('","')[0])
        self.assertTrue('Class Title' in
                       response.content.split('\r\n')[1].split('","')[0]
                       or 'Class Title' in
                       response.content.split('\r\n')[2].split('","')[0])

    def test_type_show(self):
        Conference.objects.all().delete()
        ConferenceFactory.create()
        conf = Conference.current_conf()
        show = ShowFactory(conference=conf)
        classes = ClassFactory(conference=conf)
        for event in common_events:
            if event[0] == 'show':
                sched_event = SchedEventFactory(eventitem=show.eventitem_ptr,
                                         starttime= timezone.make_aware(
                                             event[1],
                                             timezone.get_current_timezone()))
            elif event[0] == 'class':
                sched_event = SchedEventFactory(
                    eventitem=classes.eventitem_ptr\,
                    starttime=timezone.make_aware(event[1], timezone \
                                                  .get_current_timezone()))
            sched_event.save()
        login_as(ProfileFactory(), self)

        response = self.client.get(self.url + '?event_types=Show')
        self.assertTrue('Test Show' in
                        response.content.split('\r\n')[1].split('","')[0])
        self.assertFalse('Class Title' in
                        response.content.split('\r\n')[1].split('","')[0])
