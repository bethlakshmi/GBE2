from django.http import Http404
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
    UserFactory,
    VendorFactory,
    UserMessageFactory
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location,
    make_vendor_app_purchase,
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg
)
from gbe.models import UserMessage


class TestEditVendor(TestCase):
    '''Tests for edit_vendor view'''
    view_name = "vendor_edit"

    # this test case should be unnecessary, since edit_vendor should go away
    # for now, test it.

    def setUp(self):
        UserMessage.objects.all().delete()
        self.factory = RequestFactory()
        self.client = Client()
        self.user = ProfileFactory().user_object

    def get_vendor_form(self, submit=False, invalid=False):
        form = {'thebiz-profile': 1,
                'thebiz-title': 'title here',
                'thebiz-description': 'description here',
                'thebiz-physical_address': '123 Maple St.',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['thebiz-description'])
        return form

    def post_edit_paid_vendor_submission(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        make_vendor_app_purchase(vendor.conference, vendor.profile.user_object)
        response = self.client.post(url, data, follow=True)
        return response

    def post_edit_paid_vendor_draft(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form()
        data['thebiz-profile'] = vendor.profile.pk
        response = self.client.post(url, data, follow=True)
        return response

    def test_edit_vendor_no_vendor(self):
        '''Should get 404 if no valid vendor ID'''
        url = reverse(self.view_name,
                      args=[0],
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_edit_vendor_no_profile(self):
        vendor = VendorFactory()
        login_as(UserFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual(location(response), 'http://testserver/profile')

    def test_edit_vendor_wrong_user(self):
        vendor = VendorFactory()
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_vendor_edit_post_form_not_valid(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(invalid=True)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Edit Your Vendor Application' in response.content)

    def test_vendor_edit_post_form_valid(self):
        response = self.post_edit_paid_vendor_draft()
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Profile View" in response.content)

    def test_vendor_edit_post_form_valid_submit_not_paid(self):
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Vendor Payment" in response.content)

    def test_vendor_edit_post_form_valid_submit_paid_wrong_conf(self):
        vendor = VendorFactory()
        make_vendor_app_purchase(
            ConferenceFactory(
                status="completed"),
            vendor.profile.user_object)
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        data = self.get_vendor_form(submit=True)
        data['thebiz-profile'] = vendor.profile.pk
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Vendor Payment" in response.content)

    def test_edit_bid_get(self):
        '''edit_bid, not post, should take us to edit process'''
        vendor = VendorFactory()
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            '<h2 class="subtitle">Edit Your Vendor Application</h2>'
            in response.content)

    def test_edit_bid_get_no_help(self):
        '''edit_bid, not post, should take us to edit process'''
        vendor = VendorFactory(
            help_times="",
            help_description="")
        login_as(vendor.profile, self)
        url = reverse(self.view_name, urlconf='gbe.urls', args=[vendor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            '<h2 class="subtitle">Edit Your Vendor Application</h2>'
            in response.content)

    def test_vendor_submit_make_message(self):
        response = self.post_edit_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_submit_msg)

    def test_vendor_draft_make_message(self):
        response = self.post_edit_paid_vendor_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_vendor_draft_msg)

    def test_vendor_submit_has_message(self):
        msg = UserMessageFactory(
            view='EditVendorView',
            code='SUBMIT_SUCCESS')
        response = self.post_edit_paid_vendor_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_vendor_draft_has_message(self):
        msg = UserMessageFactory(
            view='EditVendorView',
            code='DRAFT_SUCCESS')
        response = self.post_edit_paid_vendor_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
