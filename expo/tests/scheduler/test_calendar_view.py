import nose.tools as nt
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test import Client
from scheduler.views import calendar_view
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from gbe.models import Conference
from pytz import utc
from datetime import (
    datetime,
    date,
)


def schedule_show(show):
    sEvent = SchedEventFactory.create(
        eventitem=show.eventitem_ptr,
        starttime=utc.localize(datetime(2016, 02, 06, 20, 0, 0)))
    room = RoomFactory.create()
    location = LocationFactory.create(_item=room.locationitem_ptr)
    ResourceAllocationFactory.create(event=sEvent,
                                     resource=location)


def test_calendar_view_shows_current_conf_by_default():
    Conference.objects.all().delete()
    current_conference = ConferenceFactory()
    other_conference = ConferenceFactory(
        status='completed')
    current_conf_day = ConferenceDayFactory(
        conference=current_conference,
        day=date(2016, 02, 06))
    other_conf_day = ConferenceDayFactory(
        conference=other_conference,
        day=date(2015, 02, 06))

    show = ShowFactory.create(conference=current_conference)
    other_show = ShowFactory.create(conference=other_conference)
    schedule_show(show)
    schedule_show(other_show)
    request = RequestFactory().get(reverse('calendar_view',
                                           urlconf="scheduler.urls"))
    request.user = ProfileFactory.create().user_object
    request.session = {'cms_admin_site': 1}
    request.GET = {'conf_slug': current_conference.conference_slug}
    response = calendar_view(request)
    nt.assert_true(show.title in response.content)
    nt.assert_false(other_show.title in response.content)


def test_no_conference_days():
    Conference.objects.all().delete()
    ConferenceFactory(status='upcoming')
    url = reverse('calendar_view_day',
                  urlconf='scheduler.urls',
                  kwargs={'event_type': 'Class',
                          'day': 'Sunday'})
    client = Client()
    response = client.get(url)
    nt.assert_true('Event Calendar' in response.content)
