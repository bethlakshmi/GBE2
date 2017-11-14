from django.test import (
    TestCase,
    Client
)
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    WorkerFactory,
)
from tests.contexts import ClassContext
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_email_template_used,
    grant_privilege,
    login_as,
)
from django.shortcuts import get_object_or_404
from gbe.models import Volunteer
from gbetext import (
    no_profile_msg,
    no_login_msg,
    full_login_msg,
    set_favorite_msg,
    unset_favorite_msg,
)


class TestSetFavorite(TestCase):
    view_name = "set_favorite"

    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()
        self.context = ClassContext()
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk, "on"],
            urlconf="gbe.scheduling.urls")

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            full_login_msg % (no_login_msg, reverse(
                'login',
                urlconf='gbe.urls') + "?next=" + self.url))

    def test_unfinished_user(self):
        unfinished = UserFactory()
        login_as(unfinished, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            no_profile_msg)

    def test_show_interest(self):
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, self.context.bid.e_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            set_favorite_msg)

    def test_remove_interest(self):
        self.url = reverse(
            self.view_name,
            args=[self.context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        ResourceAllocationFactory(event=self.context.sched_event,
                                  resource=WorkerFactory(_item=self.profile,
                                                         role="Interested"))
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('home', urlconf='gbe.urls')
        self.assertRedirects(response, redirect_url)
        self.assertNotContains(response, self.context.bid.e_title)
        assert_alert_exists(
            response,
            'success',
            'Success',
            unset_favorite_msg)
