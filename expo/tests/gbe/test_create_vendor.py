from django.shortcuts import get_object_or_404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import create_vendor
from tests.factories import gbe_factories as factories


class TestCreateVendor(TestCase):
    '''Tests for create_vendor view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_vendor_form(self, submit=False, invalid=False):
        form = {'profile': 1,
                'title': 'title here',
                'description': 'description here',
                'physical address': '123 Maple St.',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['description'])
        return form

    def test_create_vendor_no_profile(self):
        request = self.factory.get('vendor/bid/')
        request.user = factories.UserFactory.create()
        response = create_vendor(request)
        nt.assert_equal(response.status_code, 302)

    def t_create_vendor_post_no_submit(self):
        request = self.factory.get('vendor/bid/')
        request.method = 'POST'
        request.user = factories.ProfileFactory.create().user_object
        request.POST = self.get_vendor_form()
        nt.set_trace()
        response = create_vendor(request)
        # form ends up invalid - why?
        nt.assert_equal(response.status_code, 302)

    def test_create_vendor_post_form_invalid(self):
        request = self.factory.get('vendor/bid/')
        request.method = 'POST'
        request.user = factories.ProfileFactory.create().user_object
        request.POST = self.get_vendor_form(invalid=True)
        request.session = {'cms_admin_site':1}
        response = create_vendor(request)
        nt.assert_equal(response.status_code, 200)

    def test_create_vendor_no_post(self):
        request = self.factory.get('vendor/bid/')
        request.user = factories.ProfileFactory.create().user_object
        request.session = {'cms_admin_site':1}
        response = create_vendor(request)
        nt.assert_equal(response.status_code, 200)
