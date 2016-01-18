from gbe.models import (
    Conference
)

from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
    ShowFactory,
    GenericEventFactory,
)
from tests.factories.scheduler_factories import (
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

    opp = GenericEventFactory(type="Volunteer")
    opp_sevent = SchedEventFactory(eventitem=opp.eventitem_ptr)
    opp_container = EventContainerFactory(parent_event=show_sevent,
                                          child_event=opp_sevent)
    volunteer = ProfileFactory()
    worker = WorkerFactory(_item=volunteer.workeritem_ptr)
    ResourceAllocationFactory(resource=worker,
                              event=opp_sevent)

    staff_profile = ProfileFactory()
    grant_privilege(staff_profile, "Scheduling Mavens")
    request = RequestFactory().get(reverse('edit_event',
                                           urlconf="scheduler.urls",
                                           args = [show_sevent.pk,
                                                   'Show']))
    request.user = staff_profile.user
    response = edit_event(request, show_sevent.pk, event_type='Show')
    ne.assert_true(opp.name in response.content)
    show_date = show_sevent.start_time.strftime("%Y-%m-%d")
    expected_string = 'selected="selected">%s</option>' % show_date
    ne.assert_true(expected_string in response.content)
