import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_vendor
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestReviewVendor(TestCase):
    '''Tests for review_vendor view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Vendor Reviewers')

    def test_review_vendor_all_well(self):
        vendor = VendorFactory()
        url = reverse('vendor_review',
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_vendor_old_conference(self):
        old_conf = ConferenceFactory(status='completed',
                                     accepting_bids=False)
        vendor = VendorFactory(conference=old_conf)
        url = reverse('vendor_review',
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)

    def test_review_vendor_post_valid_form(self):
        vendor = VendorFactory()
        url = reverse('vendor_review',
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {'vote': 3,
                'notes': "notes",
                'bid': vendor.pk,
                'evaluator': self.privileged_profile.pk}

        response = self.client.post(url, data, follow=True)
        nt.assert_equal(200, response.status_code)
        nt.assert_true("Bid Information" in response.content)

    def test_review_vendor_all_well_vendor_coordinator(self):
        vendor = VendorFactory()
        user = ProfileFactory().user_object
        grant_privilege(user, 'Vendor Reviewers')
        grant_privilege(user, 'Vendor Coordinator')
        login_as(user, self)
        url = reverse('vendor_review',
                      args=[vendor.pk],
                      urlconf='gbe.urls')
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
