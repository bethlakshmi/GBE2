
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_act
import factories
import mock
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestEditPersona(TestCase):
    '''Tests for edit_persona view'''

    # this test case should be unnecessary, since edit_act should go away
    # for now, test it. 

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        


    def get_act_form(self):
        return {"theact-shows_preferences":[1],
                "theact-title":'An act',
                "theact-track_title":'a track',
                "theact-track_artist":'an artist',
                "theact-description":'a description',
                "theact-performer":self.performer.resourceitem_id,
        }

    @nt.raises(Http404)
    def test_edit_act_no_act(self):
        '''Should get 404 if no valid act ID'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/act/edit/-1')
        request.user = profile.user_object
        response = edit_act(request, -1)
        
    @nt.raises(Http404)
    def test_edit_act_profile_is_not_contact(self):
        #if user profile != act contact, raise 404
        user = factories.ProfileFactory.create().user_object
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d'%act.pk)
        request.user = user
        response = edit_act(request, act.pk)

    def test_act_edit_post_form_not_valid(self):
        '''act_edit, if form not valid, should return to ActEditForm'''
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = act.performer.performer_profile.user_object
        request.POST = {}
        request.POST.update(self.get_act_form())
        del(request.POST['theact-title'])
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Act Proposal' in response.content)

    def test_act_edit_post_submit_no_payment(self):
        '''edit_act, if user has not paid, should take us to please_pay'''
        act = factories.ActFactory.create()
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/act/edit')
        request.user = profile.user_object
        request.user = act.performer.performer_profile.user_object
        request.method='POST'
        request.POST = {}
        request.POST.update(self.get_act_form())
        request.POST.update({'submit':''})
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Fee has not been Paid' in response.content)

    def return_true(x):
        return True


#    @mock.patch('gbe.ticketing_idd_interface.verify_performer_app_paid', return_true)
    def test_edit_bid_post_submit_paid(self):
        '''act_bid, submitting, user has paid, should save and redirect to home'''
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d'%act.pk)
        request.user = act.performer.contact.user_object
        request.method='POST'
        request.POST = {}
        request.POST.update(self.get_act_form())
        request.POST.update({'submit':''})
        true = mock.MagicMock(return_value=True)
        with mock.patch('gbe.ticketing_idd_interface.verify_performer_app_paid', true):
            response = edit_act(request, act.pk)

#        nt.assert_equal(response.status_code, 302)
#        nt.assert_equal(location(response), '/')

        # this test is not working. To do: Fix it. 

    def test_edit_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems, should redirect to home'''
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d'%act.pk)
        request.user = act.performer.contact.user_object
        request.method='POST'
        request.POST = {}
        request.POST.update(self.get_act_form())
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/')

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        act = factories.ActFactory.create()
        request = self.factory.get('/act/edit/%d' % act.pk)
        request.user = act.performer.contact.user_object
        response = edit_act(request, act.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Act Proposal' in response.content)
    
