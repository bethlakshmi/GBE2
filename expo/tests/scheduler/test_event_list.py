from django.core.urlresolvers import reverse
import nose.tools as nt
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
    ClassFactory,
    ShowFactory,
)
from gbe.models import Conference
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
)
from tests.factories.scheduler_factories import (
    SchedEventFactory,
)
from tests.contexts import (
    ClassContext,
)


class TestEventList(TestCase):
    view_name = 'event_schedule'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_success(self):
        SchedEventFactory()
        SchedEventFactory(eventitem=ClassFactory())
        SchedEventFactory(eventitem=ShowFactory())
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        assert 'Select event type to schedule' in response.content
        assert ('<option value="GenericEvent">GenericEvent</option>'
                in response.content)
        nt.assert_true(
            '<option value="Class">Class</option>' in response.content)
        nt.assert_true(
            '<option value="Show">Show</option>' in response.content)

    def test_good_user_post_class(self):
        Conference.objects.all().delete()
        context = ClassContext()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.post(url,
                                    data={'event_type': 'Class'})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(
            context.sched_event.eventitem.describe in response.content)

    def test_good_user_post_genericevent(self):
        Conference.objects.all().delete()
        event = SchedEventFactory()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.post(url,
                                    data={'event_type': 'GenericEvent'})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(
            event.eventitem.describe in response.content)

    def test_good_user_post_show(self):
        Conference.objects.all().delete()
        show = ShowFactory()
        show_event = SchedEventFactory.create(eventitem=show.eventitem_ptr)
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.post(url,
                                    data={'event_type': 'Show'})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(
            show_event.eventitem.describe in response.content)

    def test_good_user_post_event(self):
        Conference.objects.all().delete()
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.post(url,
                                    data={'event_type': 'Event'})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(
            "Events Information" in response.content)
