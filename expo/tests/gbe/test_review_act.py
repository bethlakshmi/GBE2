from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    clear_conferences,
    current_conference,
    grant_privilege,
    login_as,
    reload,
)


class TestReviewAct(TestCase):
    '''Tests for review_act view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        grant_privilege(self.privileged_user, 'Act Coordinator')

    def test_review_act_all_well(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_act_act_reviewer(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        staff_user = ProfileFactory()
        grant_privilege(staff_user, 'Act Reviewers')
        login_as(staff_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
        nt.assert_false('Bid Control for Coordinator' in response.content)

    def test_hidden_fields_are_populated(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        staff_user = ProfileFactory()
        grant_privilege(staff_user, 'Act Reviewers')
        login_as(staff_user, self)
        response = self.client.get(url)
        evaluator_input = ('<input id="id_evaluator" name="evaluator" '
                           'type="hidden" value="%d" />') % staff_user.pk
        bid_id_input = ('<input id="id_bid" name="bid" type="hidden" '
                        'value="%d" />') % act.pk
        nt.assert_true(evaluator_input in response.content)
        nt.assert_true(bid_id_input in response.content)

    def test_review_act_old_act(self):
        conference = ConferenceFactory(status="completed",
                                       accepting_bids=False)
        act = ActFactory(conference=conference)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Review Bids' in response.content)

    def test_review_act_non_privileged_user(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(403, response.status_code)

    def test_review_act_act_post(self):
        clear_conferences()
        conference = ConferenceFactory(accepting_bids=True,
                                       status='upcoming')
        # conference = current_conference()
        act = ActFactory(accepted=1,
                         conference=conference)
        profile = ProfileFactory()
        user = profile.user_object
        grant_privilege(user, 'Act Reviewers')
        login_as(user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        response = self.client.post(url,
                                    {'vote': 3,
                                     'notes': "blah blah",
                                     'evaluator': profile.pk,
                                     'bid': act.pk},
                                    follow=True)
        nt.assert_equal(response.status_code, 200)
        expected_string = ("Bid Information for %s" %
                           conference.conference_name)
        error_string = "There is an error on the form"
        nt.assert_true(expected_string in response.content)
        nt.assert_false(error_string in response.content)

    def test_review_act_act_post_invalid_form(self):
        clear_conferences()
        conference = ConferenceFactory(accepting_bids=True,
                                       status='upcoming')
        # conference = current_conference()
        act = ActFactory(accepted=1,
                         conference=conference)
        profile = ProfileFactory()
        user = profile.user_object
        grant_privilege(user, 'Act Reviewers')
        login_as(user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        response = self.client.post(url,
                                    {'vote': 3,
                                     'notes': "blah blah",
                                     'bid': act.pk},
                                    follow=True)
        nt.assert_equal(response.status_code, 200)
        expected_string = "There is an error on the form."
        nt.assert_true(expected_string in response.content)
