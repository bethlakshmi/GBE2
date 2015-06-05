from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.contrib.auth.models import Group
from gbe.views import edit_vendor
import factories
import mock
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestEditVendor(TestCase):
    '''Tests for edit_vendor view'''

    # this test case should be unnecessary, since edit_vendor should go away
    # for now, test it. 

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_vendor_form(self, submit=False, invalid=False):
        form = {'profile':1,
                'title':'title here',
                'description':'description here',
                'physical address':'123 Maple St.',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['description'])
        return form

    @nt.raises(Http404)
    def test_edit_vendor_no_vendor(self):
        '''Should get 404 if no valid vendor ID'''
        profile = factories.ProfileFactory.create()
        request = self.factory.get('/vendor/edit/-1')
        request.user = profile.user_object
        response = edit_vendor(request, -1)
        
    @nt.raises(Http404)
    def test_edit_vendor_profile_is_not_coordinator(self):
        user = factories.ProfileFactory.create().user_object
        vendor = factories.VendorFactory.create()
        request = self.factory.get('/vendor/edit/%d'%vendor.pk)
        request.user = user
        response = edit_vendor(request, vendor.pk)

#    def test_vendor_edit_post_form_not_valid(self):
#        '''vendor_edit, if form not valid, should return to VendorEditForm'''
#        vendor = factories.VendorFactory.create()
#        request = self.factory.get('/vendor/edit/%d' % vendor.pk)
#        request.user = self.privileged_user
#        request.POST = {}
#        request.POST.update(self.get_vendor_form())
#        response = edit_vendor(request, vendor.pk)
#        nt.assert_equal(response.status_code, 200)
#        nt.assert_true('Edit Your Vendor Proposal' in response.content)

#    def test_vendor_edit_post_form_valid(self):
#        '''vendor_edit, if form not valid, should return to ActEditForm'''
#        vendor = factories.VendorFactory.create()
#        request = self.factory.get('/vendor/edit/%d' % vendor.pk)
#        request.user = self.privileged_user
#        request.POST = {}
#        request.POST.update(self.get_vendor_form())
#        nt.set_trace()
#        response = edit_vendor(request, vendor.pk)
#        nt.assert_equal(response.status_code, 302)

#    def test_edit_bid_not_post(self):
#        '''edit_bid, not post, should take us to edit process'''
#        vendor = factories.VendorFactory.create()
#        request = self.factory.get('/vendor/edit/%d' % vendor.pk)
#        request.user = self.privileged_user
#        response = edit_vendor(request, vendor.pk)
#        nt.assert_equal(response.status_code, 200)
#        nt.assert_true('Edit Your Vendor Proposal' in response.content)
    
