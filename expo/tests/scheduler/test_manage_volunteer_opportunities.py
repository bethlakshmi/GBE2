from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
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
    StaffAreaContext,
)


class TestEventList(TestCase):
    view_name = 'manage_opps'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["1"])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["1"])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_not_post(self):
        context = StaffAreaContext()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[context.sched_event.pk])
        response = self.client.get(url, follow=True)
        assert_redirects(response, reverse('edit_event',
                                              urlconf='scheduler.urls',
                                              args=['GenericEvent',
                                                    context.sched_event.pk]))
