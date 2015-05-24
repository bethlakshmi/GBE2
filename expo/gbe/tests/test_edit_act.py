from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_class
import factories
import mock
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestEditClass(TestCase):
    '''Tests for edit_class view'''

    # this test case should be unnecessary, since edit_class should go away
    # for now, test it. 

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_class_form(self):
        return {"teacher":2,
                "title":'A class',
                "description":'a description',
                "length_minutes":60,
                'maximum_enrollment':20,
                'fee':0,
        }        

    @nt.raises(Http404)
    def test_edit_class_no_class(self):
        '''Should get 404 if no valid class ID'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/class/edit/-1')
        request.user = profile.user_object
        response = edit_class(request, -1)
        
    @nt.raises(Http404)
    def test_edit_class_profile_is_not_contact(self):
        user = factories.ProfileFactory.create().user_object
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/edit/%d'%klass.pk)
        request.user = user
        response = edit_class(request, klass.pk)

    def test_class_edit_post_form_not_valid(self):
        '''class_edit, if form not valid, should return to ActEditForm'''
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/edit/%d' % klass.pk)
        request.user = klass.teacher.performer_profile.user_object
        request.POST = {}
        request.POST.update(self.get_class_form())
        del(request.POST['title'])
        response = edit_class(request, klass.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Class Proposal' in response.content)

    def test_edit_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems, should redirect to home'''
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/edit/%d' % klass.pk)
        request.user = klass.teacher.contact.user_object
        request.method='POST'
        request.POST = {}
        request.POST.update(self.get_class_form())
        response = edit_class(request, klass.pk)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), '/')

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        klass = factories.ClassFactory.create()
        request = self.factory.get('/class/edit/%d' % klass.pk)
        request.user = klass.teacher.contact.user_object
        response = edit_class(request, klass.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Class Proposal' in response.content)
    
