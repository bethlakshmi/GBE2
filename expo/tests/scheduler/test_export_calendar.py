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
    Room
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import (
    ShowContext
)

from tests.functions.scheduler_functions import (
    assert_good_sched_event_form,
    assert_selected,
    get_sched_event_form
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
        self.url = reverse(self.view_name, 
                           urlconf="scheduler.urls")
        self.showcontext = ShowContext(conference=conference)

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
            (response.content.split('\r\n')[1].split('","'))) == 8 )
        self.assertTrue('Test Show' in \
                        response.content.split('\r\n')[1].split('","')[0])
