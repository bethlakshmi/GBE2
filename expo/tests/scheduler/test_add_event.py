from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    GenericEventFactory,
    ProfileFactory,
    RoomFactory
)
from scheduler.models import EventContainer
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    StaffAreaContext,
)


class TestAddEvent(TestCase):
    view_name = 'create_event'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.eventitem = GenericEventFactory()

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.pk])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.pk])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.pk+1])
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 404)
