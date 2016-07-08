from django.http import Http404
from django.core.urlresolvers import reverse
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    location,
)


class TestEditVendor(TestCase):
    '''Tests for edit_vendor view'''
    view_name = "vendor_edit"

    # this test case should be unnecessary, since edit_vendor should go away
    # for now, test it.

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = ProfileFactory().user_object

    def get_vendor_form(self, submit=False, invalid=False):
        form = {'thebiz-profile': 1,
                'thebiz-b_title': 'title here',
                'thebiz-b_description': 'description here',
                'thebiz-physical_address': '123 Maple St.',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['thebiz-b_description'])
        return form

    def test_edit_vendor_no_vendor(self):
        '''Should get 404 if no valid vendor ID'''
        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(404, response.status_code)

    def test_edit_vendor_no_profile(self):
        vendor = VendorFactory()
        login_as(UserFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        nt.assert_equal(302, response.status_code)
        nt.assert_equal(location(response), 'http://testserver/profile')

    def test_edit_vendor_wrong_user(self):
        vendor = VendorFactory()
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        nt.assert_equal(404, response.status_code)

    def test_vendor_edit_post_form_not_valid(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(invalid=True)
        response = self.client.post(url, data)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Edit Your Vendor Application' in response.content)

    def test_vendor_edit_post_form_valid(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form()
        data['thebiz-profile'] = vendor.profile.pk
        response = self.client.post(url, data, follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Profile View" in response.content)

    def test_vendor_edit_post_form_valid_submit(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        response = self.client.post(url, data, follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true("Vendor Payment" in response.content)

    # def test_edit_bid_not_post(self):
    #     '''edit_bid, not post, should take us to edit process'''
    #     vendor = VendorFactory()
    #     login_as(vendor.profile, self)
    #     url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
    #     response = self.client.get(url)
    #     nt.assert_equal(response.status_code, 200)
    #     nt.assert_true('Edit Your Vendor Proposal' in response.content)
    # leads to syntax error in edit_vendor.
