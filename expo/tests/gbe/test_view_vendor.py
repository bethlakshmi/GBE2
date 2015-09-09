import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_vendor
from tests.factories import gbe_factories as factories


class TestViewVendor(TestCase):
    '''Tests for view_vendor view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def test_view_vendor_all_well(self):
        vendor = factories.VendorFactory.create()
        request = self.factory.get('vendor/view/%d' % vendor.pk)
        request.user = vendor.profile.user_object
        response = view_vendor(request, vendor.pk)
        test_string = 'Submitted proposals cannot be modified'
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(test_string in response.content)
