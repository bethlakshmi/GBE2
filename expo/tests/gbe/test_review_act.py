from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from django.test import TestCase
from django.test import Client
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    ActBidEvaluationFactory,
    ActCastingOptionFactory,
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory,
)
from tests.functions.gbe_functions import (
    clear_conferences,
    current_conference,
    grant_privilege,
    login_as,
    reload,
)
from tests.functions.scheduler_functions import assert_selected
from gbe.models import ActBidEvaluation
from gbetext import video_options


class TestReviewAct(TestCase):
    '''Tests for review_act view'''

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        grant_privilege(self.privileged_user, 'Act Coordinator')

    def get_post_data(self,
                      bid,
                      show=None,
                      reviewer=None,
                      invalid=False):
        reviewer = reviewer or self.privileged_profile
        show = show or ShowFactory()
        data = {'primary_vote_0': show.pk,
                'primary_vote_1': 3,
                'secondary_vote_0': show.pk,
                'secondary_vote_1': 1,
                'notes': "blah blah",
                'evaluator': reviewer.pk,
                'bid': bid.pk}
        if invalid:
            del(data['bid'])
        return data

    def get_act_w_roles(self, act):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        return self.client.get(url)

    def test_review_act_all_well(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_review_act_act_reviewer(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        staff_user = ProfileFactory()
        grant_privilege(staff_user, 'Act Reviewers')
        login_as(staff_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
        self.assertTrue('Review Information' in response.content)

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
        self.assertTrue(evaluator_input in response.content)
        self.assertTrue(bid_id_input in response.content)

    def test_review_act_old_act(self):
        conference = ConferenceFactory(status="completed",
                                       accepting_bids=False)
        act = ActFactory(b_conference=conference)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('act_view', urlconf='gbe.urls', args=[act.pk]))
        self.assertTrue('Review Bids' in response.content)

    def test_review_act_non_privileged_user(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_review_act_act_post(self):
        clear_conferences()
        conference = ConferenceFactory(accepting_bids=True,
                                       status='upcoming')
        # conference = current_conference()
        act = ActFactory(accepted=1,
                         b_conference=conference)
        profile = ProfileFactory()
        user = profile.user_object
        grant_privilege(user, 'Act Reviewers')
        login_as(user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        data = self.get_post_data(act)
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        expected_string = ("Bid Information for %s" %
                           conference.conference_name)
        error_string = "There is an error on the form"
        self.assertTrue(expected_string in response.content)
        self.assertFalse(error_string in response.content)

    def test_review_act_act_post_invalid_form(self):
        clear_conferences()
        conference = ConferenceFactory(accepting_bids=True,
                                       status='upcoming')
        # conference = current_conference()
        act = ActFactory(accepted=1,
                         b_conference=conference)
        profile = ProfileFactory()
        user = profile.user_object
        grant_privilege(user, 'Act Reviewers')
        login_as(user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        data = self.get_post_data(act, invalid=True)
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        expected_string = "There is an error on the form."
        self.assertTrue(expected_string in response.content)

    def test_review_act_load_existing_review(self):
        eval = ActBidEvaluationFactory(
            evaluator=self.privileged_profile
        )
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[eval.bid.pk])
        login_as(self.privileged_user, self)

        response = self.client.get(url)

        assert_selected(
            response,
            eval.primary_vote.vote,
            "Weak Yes")
        assert_selected(
            response,
            eval.primary_vote.show.pk,
            str(eval.primary_vote.show))
        assert_selected(
            response,
            eval.secondary_vote.show.pk,
            str(eval.secondary_vote.show))

    def test_review_act_update_review(self):
        eval = ActBidEvaluationFactory(
            evaluator=self.privileged_profile
        )
        show = ShowFactory()
        login_as(self.privileged_user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[eval.bid.pk])
        data = self.get_post_data(
            eval.bid,
            reviewer=self.privileged_user,
            show=show
            )
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        evals = ActBidEvaluation.objects.filter(
            evaluator=self.privileged_profile,
            bid=eval.bid
        )
        self.assertTrue(len(evals), 1)
        self.assertTrue(evals[0].secondary_vote.vote, 1)
        self.assertTrue(evals[0].primary_vote.show, show)

    def test_video_choice_display(self):
        act = ActFactory()
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        assert 'Video Notes:' in response.content
        assert video_options[1][1] not in response.content

    def test_review_summer_act(self):
        act = ActFactory(is_summer=True)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('The Summer Act' in response.content)

    def test_review_default_role_present(self):
        act = ActFactory()
        response = self.get_act_w_roles(act)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<option value="" selected="selected">Regular Act</option>')

    def test_review_special_role_present(self):
        act = ActFactory()
        response = self.get_act_w_roles(act)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<option value="Hosted by...">Hosted by...</option>')

    def test_review_special_role_already_cast(self):
        context = ActTechInfoContext(act_role="Hosted by...")
        response = self.get_act_w_roles(context.act)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<option value="Hosted by..." selected="selected"' +
            '>Hosted by...</option>')
