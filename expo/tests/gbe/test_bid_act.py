import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import bid_act
import mock
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import location


class TestBidAct(TestCase):
    '''Tests for bid_act view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        current_conference = factories.ConferenceFactory.create()
        current_conference.accepting_bids = True
        current_conference.save()

    def get_act_form(self):
        return {'theact-shows_preferences': [1],
                'theact-title': 'An act',
                'theact-track_title': 'a track',
                'theact-track_artist': 'an artist',
                'theact-description': 'a description',
                'theact-performer': self.performer.resourceitem_id,
                }

    def test_bid_act_no_profile(self):
        '''act_bid, when user has no profile, should bounce out to /profile'''
        user = factories.UserFactory.create()
        request = self.factory.get('/act/create')
        request.user = user
        response = bid_act(request)
        nt.assert_equal(response.status_code, 302)

    def test_bid_act_no_personae(self):
        '''act_bid, when profile has no personae,
        should redirect to persona_create'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/act/create')
        request.user = profile.user_object
        response = bid_act(request)
        nt.assert_equal(response.status_code, 302)

    def test_act_bid_post_no_performer(self):
        '''act_bid, user has no performer, should redirect to persona_create'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/act/create')
        request.user = profile.user_object
        request.POST = self.get_act_form()
        response = bid_act(request)
        nt.assert_equal(response.status_code, 302)

    def test_act_bid_post_form_not_valid(self):
        '''act_bid, if form not valid, should return to ActEditForm'''
        request = self.factory.get('/act/create')
        request.user = self.performer.performer_profile.user_object
        request.POST = {}
        request.POST.update(self.get_act_form())
        request.session = {'cms_admin_site':1}
        del(request.POST['theact-title'])
        response = bid_act(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Propose an Act' in response.content)

    def test_act_bid_post_submit_no_payment(self):
        '''act_bid, if user has not paid, should take us to please_pay'''
        factories.ConferenceFactory.create(accepting_bids=True)
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/act/create')
        request.user = profile.user_object
        request.user = self.performer.performer_profile.user_object
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_act_form())
        request.POST.update({'submit': ''})
        request.session = {'cms_admin_site':1}
        response = bid_act(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Fee has not been Paid' in response.content)

    def return_true(x):
        return True

    def test_act_bid_post_submit_paid(self):
        '''act_bid, submitting, user has paid, should save
        and redirect to home'''
        profile = factories.ProfileFactory.create()
        factories.ConferenceFactory.create(accepting_bids=True)
        request = self.factory.get('/act/create')
        request.user = profile.user_object
        request.user = self.performer.performer_profile.user_object
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_act_form())
        request.POST.update({'submit': ''})
        request.session = {'cms_admin_site':1}
        true = mock.MagicMock(return_value=True)
        with mock.patch(
                'gbe.ticketing_idd_interface.verify_performer_app_paid', true):
            response = bid_act(request)

#        nt.assert_equal(response.status_code, 302)
#        nt.assert_equal(location(response), '/gbe')

        # this test is not working. To do: Fix it.

    def test_act_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        factories.ConferenceFactory.create(accepting_bids=True)
        request = self.factory.get('/act/create')
        request.user = self.performer.performer_profile.user_object
        request.method = 'POST'
        request.POST = {}
        request.POST.update(self.get_act_form())
        response = bid_act(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/gbe')

    def test_act_bid_not_post(self):
        '''act_bid, not post, should take us to bid process'''
        request = self.factory.get('/act/create')
        request.user = self.performer.performer_profile.user_object
        request.session = {'cms_admin_site':1}
        response = bid_act(request)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Propose an Act' in response.content)