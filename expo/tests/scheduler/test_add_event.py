from django.core.urlresolvers import reverse
import nose.tools as nt
from django_nose.tools import assert_redirects
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ClassFactory,
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
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 403)

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id+1])
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 404)

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["GenericEvent", self.eventitem.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(self.eventitem.title,
                     response.content)
        nt.assert_in(self.eventitem.description,
                     response.content)
        nt.assert_in(str(self.eventitem.duration),
                     response.content)

    def test_good_user_get_class(self):
        login_as(self.privileged_profile, self)
        klass = ClassFactory()
        url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=["Class", klass.eventitem_id])
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_in(klass.title,
                     response.content)
        nt.assert_in(klass.description,
                     response.content)
        nt.assert_in("1:00",
                     response.content)
        nt.assert_in(str(klass.teacher),
                     response.content)
