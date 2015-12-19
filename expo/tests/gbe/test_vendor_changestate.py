from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import vendor_changestate
from tests.factories import gbe_factories as factories
from tests.factories.gbe_factories import (
    VendorFactory,
    ProfileFactory
)
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group


class TestVendorChangestate(TestCase):
    '''Tests for vendor_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.vendor = VendorFactory.create()
        self.privileged_user = ProfileFactory.create().user_object
        group, nil = Group.objects.get_or_create(name='Vendor Coordinator')
        self.privileged_user.groups.add(group)

    def test_vendor_changestate_authorized_user(self):
        '''The proper coordinator is changing the state, it works'''
        request = self.factory.get('vendor/changestate/%d' % self.vendor.pk)
        request.user = self.privileged_user
        response = vendor_changestate(request, self.vendor.pk)
        nt.assert_equal(response.status_code, 302)

    @nt.raises(PermissionDenied)
    def test_vendor_changestate_unauthorized_user(self):
        '''A regular user is changing the state, it fails'''
        request = self.factory.get('vendor/changestate/%d' % self.vendor.pk)
        request.user = ProfileFactory.create().user_object
        response = vendor_changestate(request, self.vendor.pk)
