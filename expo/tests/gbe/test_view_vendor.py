
from django.core.exceptions import PermissionDenied
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_vendor
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    VendorFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestViewVendor(TestCase):
    '''Tests for view_vendor view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()

    def test_view_vendor_all_well(self):
        vendor = VendorFactory.create()
        request = self.factory.get('vendor/view/%d' % vendor.pk)
        request.user = vendor.profile.user_object
        request.session = {'cms_admin_site': 1}
        response = view_vendor(request, vendor.pk)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)



    def test_view_vendor_privileged_user(self):
        vendor = VendorFactory.create()
        staff_user = ProfileFactory.create()
        grant_privilege(staff_user, "Vendor Reviewers")
        login_as(staff_user, self)
        request = self.factory.get('vendor/view/%d' % vendor.pk)
        request.user = staff_user.user_object
        request.session = {'cms_admin_site': 1}
        response = view_vendor(request, vendor.pk)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)


    @nt.raises(PermissionDenied)
    def test_view_vendor_wrong_user(self):
        vendor = VendorFactory.create()
        request = self.factory.get('vendor/view/%d' % vendor.pk)
        request.user = ProfileFactory().user_object
        request.session = {'cms_admin_site': 1}
        response = view_vendor(request, vendor.pk)
