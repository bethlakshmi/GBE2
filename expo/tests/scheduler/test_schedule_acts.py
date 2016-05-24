from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from scheduler.models import EventItem
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import ShowContext


class TestDeleteEvent(TestCase):
    view_name = 'schedule_acts'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.context = ShowContext()
        self.url = reverse(self.view_name,
                           urlconf="scheduler.urls",
                           args=[self.context.show.title])

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_show(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="scheduler.urls",
            args=["Bad bad event name"])
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_good_user_get_no_show(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="scheduler.urls")
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select event type to schedule")
        self.assertContains(
            response,
            '<option value="' + self.context.show.title +
            '">' + self.context.show.title +
            '</option>')

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<ul class="errorlist">', response.content)
        self.assertIn(self.context.show.title, response.content)
