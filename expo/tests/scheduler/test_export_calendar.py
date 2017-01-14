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


class TestExportCalendar(TestCase):
    view_name = 'export_calendar'

    def setUp(self):
        self.client = Client()
        conference = ConferenceFactory()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.show = ShowFactory()
        self.classes = ClassFactory()
        self.url = reverse(self.view_name,
                           urlconf="scheduler.urls")
        self.showcontext = ShowContext(conference=conference)
        self.classcontext = ClassContext(conference=conference)

    def test_no_login(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_schedule(self):
        Conference.objects.all().delete()
        show = ShowFactory()
        SchedEventFactory.create(eventitem=show.eventitem_ptr)
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertTrue(response.content.count('\n') == 1)
        self.assertTrue('Session Title' in response.content)

    def test_schedule(self):
        login_as(ProfileFactory(), self)
        room = RoomFactory()
        show = ShowFactory()
        show_sevent = SchedEventFactory(eventitem=show.eventitem_ptr)
        response = self.client.get(self.url)
        self.assertTrue(response.content.count('\n') > 1)
        self.assertTrue(len(
            (response.content.split('\r\n')[1].split('","'))) >= 8)
        self.assertTrue('Test Show' in
                        response.content.split('\r\n')[1].split('","')[0])

    def test_guidebook(self):
        login_as(ProfileFactory(), self)
        room = RoomFactory()
        show = ShowFactory()
        classes = ClassFactory()
        show_sevent = SchedEventFactory(eventitem=show.eventitem_ptr)
        class_sevent = SchedEventFactory(eventitem=classes.eventitem_ptr)
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
        login_as(ProfileFactory(), self)
        room = RoomFactory()
        show = ShowFactory()
        classes = ClassFactory()
        show_sevent = SchedEventFactory(eventitem=show.eventitem_ptr)
        class_sevent = SchedEventFactory(eventitem=classes.eventitem_ptr)
        response = self.client.get(self.url + '?cal_format=ical')
        self.assertTrue('BEGIN:VCALENDAR' in
                        response.content.split('\r\n')[0])
        vevent_count = 0
        for line in response.content.split('\r\n'):
            if 'BEGIN:VEVENT' in line:
                vevent_count = vevent_count + 1
        self.assertTrue(vevent_count > 0)

    def test_day_all(self):
        login_as(ProfileFactory(), self)
        room = RoomFactory()
        show = ShowFactory()
        classes = ClassFactory()
        show_sevent = SchedEventFactory(
            eventitem=show.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 6),
            timezone.get_current_timezone()))
        class_sevent = SchedEventFactory(
            eventitem=classes.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 6),
            timezone.get_current_timezone()))
        show_sevent = SchedEventFactory(
            eventitem=show.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 7),
            timezone.get_current_timezone()))
        class_sevent = SchedEventFactory(
            eventitem=classes.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 7),
            timezone.get_current_timezone()))
        show_sevent = SchedEventFactory(
            eventitem=show.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 8),
            timezone.get_current_timezone()))
        class_sevent = SchedEventFactory(
            eventitem=classes.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 8),
            timezone.get_current_timezone()))
        response = self.client.get(self.url)
        fri_count, sat_count, sun_count = 0, 0, 0
        for line in response.content.split('\r\n'):
            print line
            if 'Feb. 6' in line:
                fri_count = fri_count + 1
            elif 'Feb. 7' in line:
                sat_count = sat_count + 1
            elif 'Feb. 8' in line:
                sun_count = sun_count + 1
        print fri_count, sat_count, sun_count
        self.assertTrue(fri_count == 2 and sat_count == 2 and sun_count == 2)

    def test_day_sat(self):
        login_as(ProfileFactory(), self)
        room = RoomFactory()
        show = ShowFactory()
        classes = ClassFactory()
        show_sevent = SchedEventFactory(
            eventitem=show.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 6),
            timezone.get_current_timezone()))
        class_sevent = SchedEventFactory(
            eventitem=classes.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 6),
            timezone.get_current_timezone()))
        show_sevent = SchedEventFactory(
            eventitem=show.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 7),
            timezone.get_current_timezone()))
        class_sevent = SchedEventFactory(
            eventitem=classes.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 7),
            timezone.get_current_timezone()))
        show_sevent = SchedEventFactory(
            eventitem=show.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 8),
            timezone.get_current_timezone()))
        class_sevent = SchedEventFactory(
            eventitem=classes.eventitem_ptr,
            starttime = timezone.make_aware(datetime(2015, 02, 8),
            timezone.get_current_timezone()))

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

    def test_type_class(self):
        login_as(ProfileFactory(), self)
        room = RoomFactory()
        show = ShowFactory()
        classes = ClassFactory()
        show_sevent = SchedEventFactory(eventitem=show.eventitem_ptr)
        class_sevent = SchedEventFactory(eventitem=classes.eventitem_ptr)
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
        login_as(ProfileFactory(), self)
        room = RoomFactory()
        show = ShowFactory()
        classes = ClassFactory()
        show_sevent = SchedEventFactory(eventitem=show.eventitem_ptr)
        class_sevent = SchedEventFactory(eventitem=classes.eventitem_ptr)
        response = self.client.get(self.url + '?event_types=Show')
        self.assertTrue('Test Show' in
                        response.content.split('\r\n')[1].split('","')[0])
        self.assertFalse('Class Title' in
                        response.content.split('\r\n')[1].split('","')[0])
