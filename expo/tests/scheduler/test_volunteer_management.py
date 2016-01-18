from tests.factories.gbe_factories import (
    ConferenceFactory,
    ConferenceDayFactory,
    GenericEventFactory,
    ProfileFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    LocationFactory,
    WorkerFactory,
    SchedEventFactory,
    EventContainerFactory,
    ResourceAllocationFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.test import (
    TestCase,
    Client
)
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from scheduler.views import edit_event
import nose.tools as nt


def test_scheduled_volunteer_opportunity_shows_day():
    show = ShowFactory()
    show_sevent = SchedEventFactory(eventitem=show.eventitem_ptr)
    ConferenceDayFactory(conference=show.conference,
                         day=show_sevent.start_time.date())
    opp = GenericEventFactory(type="Volunteer",
                              conference=show.conference)
    opp_sevent = SchedEventFactory(eventitem=opp.eventitem_ptr)
    opp_container = EventContainerFactory(parent_event=show_sevent,
                                          child_event=opp_sevent)
    volunteer = ProfileFactory()
    worker = WorkerFactory(_item=volunteer.workeritem_ptr)
    ResourceAllocationFactory(resource=worker,
                              event=opp_sevent)
    room = RoomFactory()
    location = LocationFactory(_item=room.locationitem_ptr)
    ResourceAllocationFactory(resource=location,
                              event=opp_sevent)
    staff_profile = ProfileFactory()
    grant_privilege(staff_profile, "Scheduling Mavens")
    grant_privilege(staff_profile, "Volunteer Coordinator")
    request = RequestFactory().get(reverse('edit_event',
                                           urlconf="scheduler.urls",
                                           args=['Show', show_sevent.pk]))
    request.user = staff_profile.user_object
    request.session = {'cms_admin_site': 1}
    response = edit_event(request, show_sevent.pk, event_type='Show')
    nt.assert_true(opp.title in response.content)
    show_date = show_sevent.start_time.strftime("%Y-%m-%d")
    expected_string = 'selected="selected">%s</option>' % show_date
    nt.assert_true(expected_string in response.content)
