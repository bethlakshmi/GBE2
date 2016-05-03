from django.core.urlresolvers import reverse
import nose.tools as nt
from unittest import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
)
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
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

    def test_good_user_first_load(self):
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="scheduler.urls")
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
