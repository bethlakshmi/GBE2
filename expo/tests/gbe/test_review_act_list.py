import nose.tools as nt
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    )
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
)

from django.core.exceptions import PermissionDenied


class TestReviewActList(TestCase):
    '''Tests for review_act_list view'''
    view_name = 'act_review'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        self.conference = current_conference()
        ActFactory.create_batch(4,
                                conference=self.conference,
                                submitted=True)

    def test_review_act_list_all_well(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': self.conference.conference_slug})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_act_bad_user(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(403, response.status_code)

    def test_review_act_no_profile(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(403, response.status_code)
