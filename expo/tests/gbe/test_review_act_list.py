from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_act_list
from django.contrib.auth.models import Group
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

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.privileged_profile = ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        self.conference = current_conference()
        ActFactory.create_batch(4,
                                conference=self.conference,
                                submitted=True)

    def test_review_act_all_well(self):
        request = self.factory.get('act/review/',
                                   data={'conf_slug':self.conference.conference_slug})
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_act_list(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    @nt.raises(PermissionDenied)
    def test_review_act_bad_user(self):
        request = self.factory.get('act/review/')
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_act_list(request)

    @nt.raises(PermissionDenied)
    def test_review_act_no_profile(self):
        request = self.factory.get('act/review/')
        request.user = UserFactory.create()
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_act_list(request)
