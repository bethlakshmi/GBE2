from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from django.test import (
    Client,
    TestCase,
)
from tests.contexts import (
    ClassContext,
)
from gbe.models import Conference
from scheduler.models import EventItem
from tests.functions.gbe_functions import (
    login_as,
    assert_alert_exists,
    make_admission_purchase,
)
from django.contrib.auth.models import User
from datetime import (
    datetime,
    timedelta,
)
from gbetext import (
    no_profile_msg,
    no_login_msg,
    not_purchased_msg,
    full_login_msg,
    set_favorite_msg,
    unset_favorite_msg,
)


class TestEvalEventView(TestCase):
    view_name = 'eval_event'

    def setUp(self):
        self.client = Client()
        self.context = ClassContext(starttime=datetime.now()-timedelta(days=1))
        self.context.setup_eval()
        self.profile = ProfileFactory()
        make_admission_purchase(self.context.conference,
                                self.profile.user_object,
                                include_most=True,
                                include_conference=True)
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.sched_event.pk])

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

    def test_get_eval(self):
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, self.context.bid.e_title)

    def test_no_purchase(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            not_purchased_msg)
