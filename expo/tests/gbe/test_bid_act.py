import nose.tools as nt
import mock
from gbe.ticketing_idd_interface import (
    verify_performer_app_paid,
)

from django.core.urlresolvers import reverse
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    location,
    login_as,
    current_conference,
)


class TestBidAct(TestCase):
    '''Tests for bid_act view'''
    view_name = 'act_create'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        current_conference = ConferenceFactory()
        current_conference.accepting_bids = True
        current_conference.save()

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

    def test_bid_act_no_profile(self):
        '''act_bid, when user has no profile, should bounce out to /profile'''
        user = UserFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bid_act_no_personae(self):
        '''act_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = ProfileFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 302)

    def test_bid_act_get_with_persona(self):
        '''act_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = PersonaFactory().performer_profile
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(url)
        expected_string = "Propose an Act"
        nt.assert_true(expected_string in response.content)
        nt.assert_equal(response.status_code, 200)

    def test_act_bid_post_no_performer(self):
        '''act_bid, user has no performer, should redirect to persona_create'''
        profile = ProfileFactory()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.post(url, data=self.get_act_form())
        nt.assert_equal(response.status_code, 302)

    def test_act_bid_post_form_not_valid(self):
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form(submit=True)
        del(POST['theact-description'])
        response = self.client.post(url,
                                    data=POST)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Propose an Act' in response.content)

    def test_act_bid_post_submit_no_payment(self):
        '''act_bid, if user has not paid, should take us to please_pay'''
        current_conference()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        POST.update({'submit': ''})
        response = self.client.post(url, data=POST)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Fee has not been Paid' in response.content)

    def fake_verify_performer_app_paid(user_name):
        return True

    def test_act_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        current_conference()
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        POST = self.get_act_form()
        response = self.client.post(url, data=POST)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), 'http://testserver/gbe')

    def test_act_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        url = reverse(self.view_name, urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.post(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Propose an Act' in response.content)
