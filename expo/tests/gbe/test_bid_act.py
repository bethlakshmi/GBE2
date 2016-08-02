from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    location,
    login_as,
    current_conference,
    assert_alert_exists,
    make_act_app_purchase
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
    default_act_title_conflict
)
from gbe.models import (
    Conference,
    UserMessage
)


class TestBidAct(TestCase):
    '''Tests for bid_act view'''
    view_name = 'act_create'

    def setUp(self):
        Conference.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.current_conference = ConferenceFactory(accepting_bids=True)
        UserMessage.objects.all().delete()

    def get_act_form(self, submit=False):

        form_dict = {'theact-shows_preferences': [1],
                     'theact-title': 'An act',
                     'theact-track_title': 'a track',
                     'theact-track_artist': 'an artist',
                     'theact-description': 'a description',
                     'theact-performer': self.performer.resourceitem_id,
                     }
        if submit:
            form_dict['submit'] = 1
        return form_dict

    def post_paid_act_submission(self):
        current_conference()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        POST.update({'submit': ''})
        make_act_app_purchase(self.performer.performer_profile.user_object)
        response = self.client.post(url, data=POST, follow=True)
        return response, POST

    def post_paid_act_draft(self):
        current_conference()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        response = self.client.post(url, data=POST, follow=True)
        return response, POST

    def post_title_collision(self):
        original = ActFactory(
            conference=self.current_conference,
            performer=self.performer)
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = self.get_act_form()
        data['theact-title'] = original.title
        response = self.client.post(
            url,
            data=data,
            follow=True)
        return response, original

    def test_bid_act_no_profile(self):
        '''act_bid, when user has no profile, should bounce out to /profile'''
        user = UserFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_bid_act_no_personae(self):
        '''act_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = ProfileFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_act_bid_post_no_performer(self):
        '''act_bid, user has no performer, should redirect to persona_create'''
        profile = ProfileFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.post(url, data=self.get_act_form())
        self.assertEqual(response.status_code, 302)

    def test_act_bid_post_form_not_valid(self):
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form(submit=True)
        del(POST['theact-description'])
        response = self.client.post(url,
                                    data=POST)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Propose an Act' in response.content)

    def test_act_bid_post_submit_no_payment(self):
        '''act_bid, if user has not paid, should take us to please_pay'''
        current_conference()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        POST.update({'submit': ''})
        response = self.client.post(url, data=POST)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Fee has not been Paid' in response.content)

    def test_act_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        current_conference()
        response, data = self.post_paid_act_draft()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "(Click to edit)")
        self.assertContains(response, data['theact-title'])

    def test_act_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Propose an Act' in response.content)

    def test_act_submit_paid_act(self):
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-title'])

    def test_act_submit_second_paid_act(self):
        prev_act = ActFactory(
            submitted=True,
            performer=self.performer)
        make_act_app_purchase(self.performer.performer_profile.user_object)
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View</a> act")
        self.assertContains(response, data['theact-title'])

    def test_act_submit_make_message(self):
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_act_submit_msg)

    def test_act_draft_make_message(self):
        response, data = self.post_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_act_draft_msg)

    def test_act_submit_has_message(self):
        msg = UserMessageFactory(
            view='BidActView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_paid_act_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_act_draft_has_message(self):
        msg = UserMessageFactory(
            view='BidActView',
            code='DRAFT_SUCCESS')
        response, data = self.post_paid_act_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_act_title_collision(self):
        response, original = self.post_title_collision()
        self.assertEqual(response.status_code, 200)
        error_msg = default_act_title_conflict % (
            reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[original.pk]),
            original.title)
        assert_alert_exists(
            response, 'danger', 'Error', error_msg)

    def test_act_title_collision_w_msg(self):
        message_string = "link: %s title: %s"
        msg = UserMessageFactory(
            view='BidActView',
            code='ACT_TITLE_CONFLICT',
            description=message_string)
        response, original = self.post_title_collision()
        self.assertEqual(response.status_code, 200)
        error_msg = message_string % (
            reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[original.pk]),
            original.title)
        assert_alert_exists(
            response, 'danger', 'Error', error_msg)
