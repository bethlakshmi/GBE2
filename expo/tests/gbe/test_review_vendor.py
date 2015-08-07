import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_vendor
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (login_as,
                                           is_login_page,
                                           is_profile_update_page,
                                           location)


class TestReviewVendor(TestCase):
    '''Tests for review_vendor view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()
        self.privileged_profile = factories.ProfileFactory.create()
        self.privileged_user = self.privileged_profile.user_object
        vendor_reviewers, created = Group.objects.get_or_create(name='Vendor Reviewers')
        self.privileged_user.groups.add(vendor_reviewers)

    def test_review_vendor_all_well(self):
        vendor = factories.VendorFactory.create()
        request = self.factory.get('vendor/review/%d' % vendor.pk)
        request.user = self.privileged_user
        login_as(request.user, self)
        response = review_vendor(request, vendor.pk)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Bid Information' in response.content)
