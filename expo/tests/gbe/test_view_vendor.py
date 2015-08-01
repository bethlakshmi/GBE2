import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_vendor
import factories
import mock
import gbe.ticketing_idd_interface 
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

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
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Submitted proposals cannot be modified' in response.content)
