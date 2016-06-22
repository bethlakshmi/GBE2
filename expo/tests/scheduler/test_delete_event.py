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
    clear_conferences,
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts import ClassContext


class TestDeleteEvent(TestCase):
    view_name = 'delete_event'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        clear_conferences()
        self.context = ClassContext()
        self.url = reverse(self.view_name,
                           urlconf="scheduler.urls",
                           args=["Class", self.context.bid.eventitem_id])

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

    def test_good_user_get_bad_event(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="scheduler.urls",
            args=["Class", self.context.bid.eventitem_id+1])
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_good_user_get_success(self):
        pk = self.context.bid.eventitem_id
        title = "deletable class"
        self.context.bid.title = title
        self.context.bid.save()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response,
                             reverse('event_schedule',
                                     urlconf='scheduler.urls',
                                     args=["Class"]))
        self.assertNotIn('<ul class="errorlist">', response.content)
        self.assertIn('Events Information', response.content)
        self.assertNotIn(title, response.content)
        self.assertNotIn("<a href='" + self.url + "'>Delete</a>'",
                         response.content)
