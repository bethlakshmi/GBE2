from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import vendor_changestate
from tests.factories import gbe_factories as factories
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from tests.functions.gbe_functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)


class TestVendorChangestate(TestCase):
    '''Tests for vendor_changestate view'''

    def setUp(self):
        pass

    def test_vendor_changestate(self):
        # needs a little work to test
        pass
