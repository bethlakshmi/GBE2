from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.contexts import ClassContext
from gbe.models import Conference

class TestInterest(TestCase):
    view_name = "interest"

    def setUp(self):
        self.client = Client()
        self.priv_profile = ProfileFactory()
        self.context = ClassContext()
        self.old_conference = ConferenceFactory(status="completed")
        self.old_context = ClassContext(conference=self.old_conference)
        grant_privilege(self.priv_profile, 'Class Coordinator')
        self.url = reverse(self.view_name,
                           urlconf="gbe.reporting.urls")

    def test_interest_not_visible_without_permission(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_default_conf_success(self):
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.bid.e_title)
        self.assertNotContains(response, self.old_context.bid.e_title)
        self.assertContains(response, self.context.teacher.name)
        self.assertNotContains(response, self.old_context.teacher.name)
        self.assertContains(response, self.context.room.name)
        self.assertNotContains(response, self.old_context.room.name)

    def test_interest_is_present(self):
        interested = []
        for i in range(0, 3):
            interested += [self.context.set_interest()]
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for person in interested:
            self.assertContains(
                response,
                "%s &lt;%s&gt;;</br>" % (person.display_name,
                                         person.user_object.email))
