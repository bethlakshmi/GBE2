import nose.tools as nt
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActBidEvaluationFactory,
    ActCastingOptionFactory,
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,

)
from tests.contexts import ShowContext
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
        self.url = reverse(
            self.view_name,
            urlconf='gbe.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        self.conference = current_conference()
        self.acts = ActFactory.create_batch(
            4,
            b_conference=self.conference,
            submitted=True)

    def test_review_act_list_all_well(self):
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_act_list_inactive_user(self):
        inactive = ActFactory(
            submitted=True,
            b_conference=self.conference,
            performer__contact__user_object__is_active=False)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertIn('bid-table error_row', response.content)

    def test_review_act_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        nt.assert_equal(403, response.status_code)

    def test_review_act_no_profile(self):
        login_as(UserFactory(), self)
        response = self.client.get(self.url)
        nt.assert_equal(403, response.status_code)

    def test_review_act_has_reviews(self):
        eval = ActBidEvaluationFactory(bid=self.acts[0])
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, str(eval.primary_vote.show))
        self.assertContains(response, str(eval.secondary_vote.show))
        self.assertContains(response, str(eval.bid.b_title))

    def test_review_act_assigned_show(self):
        context = ShowContext()
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        assert context.acts[0].b_title in response.content
        assert context.show.e_title in response.content

    def test_review_act_assigned_show_role(self):
        context = ShowContext(act_role="Hosted By...")
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        assert context.show.e_title in response.content
        assert "Hosted By..." in response.content

    def test_review_act_assigned_two_shows(self):
        context = ShowContext()
        context2 = ShowContext(
            conference=context.conference,
            act=context.acts[0])
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        assert context.acts[0].b_title in response.content
        assert "%s, %s" % (context.show.e_title,
                           context2.show.e_title) in response.content
