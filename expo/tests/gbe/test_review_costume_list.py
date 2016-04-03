from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    CostumeFactory,
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


class TestReviewCostumeList(TestCase):
    '''Tests for review_costume_list view'''
    view_name = "costume_review_list"

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Costume Reviewers')
        self.conference = current_conference()
        CostumeFactory.create_batch(4,
                                    conference=self.conference,
                                    submitted=True)

    def test_review_costume_all_well(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url,
            data={'conf_slug': self.conference.conference_slug})

        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_costume_bad_user(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url,
            data={'conf_slug': self.conference.conference_slug})
        nt.assert_equal(403, response.status_code)

    def test_review_costume_no_profile(self):
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(url,
            data={'conf_slug': self.conference.conference_slug})
        nt.assert_equal(403, response.status_code)
