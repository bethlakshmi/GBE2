import gbe.models as conf
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_act
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    ActFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestReviewAct(TestCase):
    '''Tests for revview_act view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.privileged_profile = ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        grant_privilege(self.privileged_user, 'Act Coordinator')

    def test_review_act_all_well(self):
        act = ActFactory.create()
        request = self.factory.get('act/review/%d' % act.pk)
        request.session = {'cms_admin_site': 1}
        request.user = self.privileged_user
        login_as(request.user, self)
        response = review_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_act_act_reviewer(self):
        act = ActFactory.create()
        request = self.factory.get('act/review/%d' % act.pk)
        request.session = {'cms_admin_site': 1}
        request.user = ProfileFactory().user_object
        grant_privilege(request.user, 'Act Reviewers')
        login_as(request.user, self)
        response = review_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_false('Bid Control for Coordinator' in response.content)

    def test_review_act_old_act(self):
        conference = ConferenceFactory(status="completed",
                                       accepting_bids=False)
        act = ActFactory.create(conference=conference)
        request = self.factory.get('act/review/%d' % act.pk)
        request.session = {'cms_admin_site': 1}
        request.user = self.privileged_user
        login_as(request.user, self)
        response = review_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Review Bids' in response.content)

    @nt.raises(PermissionDenied)
    def test_review_act_non_privileged_user(self):
        act = ActFactory.create()
        request = self.factory.get('act/review/%d' % act.pk)
        request.session = {'cms_admin_site': 1}
        request.user = ProfileFactory().user_object
        login_as(request.user, self)
        response = review_act(request, act.pk)
