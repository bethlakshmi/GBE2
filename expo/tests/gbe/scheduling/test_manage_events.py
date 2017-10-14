from django.core.urlresolvers import reverse
import nose.tools as nt
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
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
from expo.settings import (
    DATE_FORMAT,
    DATETIME_FORMAT,
)
from datetime import (
    timedelta,
)


class TestEventList(TestCase):
    view_name = 'manage_event_list'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls")
        self.day = ConferenceDayFactory()


    def test_no_login_gives_error(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_success(self):
        old_conf_day = ConferenceDayFactory(
            conference__status="completed",
            day=self.day.day + timedelta(3))
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        s = '<li role="presentation" class="active">\n' + \
        '   <a href = "%s">%s</a></li>'
        self.assertContains(
            response,
            s % (self.day.conference.conference_slug,
                 self.day.conference.conference_slug))
        s = '<li role="presentation" >\n   <a href = "%s">%s</a></li>'
        self.assertContains(
            response,
            s % (old_conf_day.conference.conference_slug,
                 old_conf_day.conference.conference_slug))
        self.assertContains(
            response,
            self.day.day.strftime(DATE_FORMAT))
        self.assertNotContains(
            response,
            old_conf_day.day.strftime(DATE_FORMAT))

    def test_good_user_get_success_pick_conf(self):
        old_conf_day = ConferenceDayFactory(
            conference__status="completed",
            day=self.day.day + timedelta(3))
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[old_conf_day.conference.conference_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        s = '<li role="presentation" class="active">\n' + \
        '   <a href = "%s">%s</a></li>'
        self.assertContains(
            response,
            s % (old_conf_day.conference.conference_slug,
                 old_conf_day.conference.conference_slug))
        s = '<li role="presentation" >\n   <a href = "%s">%s</a></li>'
        self.assertContains(
            response,
            s % (self.day.conference.conference_slug,
                 self.day.conference.conference_slug))
        self.assertContains(
            response,
            old_conf_day.day.strftime(DATE_FORMAT))
        self.assertNotContains(
            response,
            self.day.day.strftime(DATE_FORMAT))
