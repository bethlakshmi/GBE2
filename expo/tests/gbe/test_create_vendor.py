from django.core.urlresolvers import reverse
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import create_vendor
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    current_conference,
    login_as,
    location,
)

class TestCreateVendor(TestCase):
    '''Tests for create_vendor view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()
        self.conference = current_conference()

    def get_vendor_form(self, submit=False, invalid=False):
        form = {'profile': 1,
                'title': 'title here',
                'description': 'description here',
                'physical_address': '123 Maple St.',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['description'])
        return form

    def test_create_vendor_no_profile(self):
        url = reverse('vendor_create', urlconf='gbe.urls')
        login_as(UserFactory.create(), self)
        response = self.client.get(url, follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Update Your Profile' in response.content)


    def test_create_vendor_post_form_valid(self):
        url = reverse('vendor_create', urlconf='gbe.urls')
        profile = ProfileFactory()
        login_as(profile, self)
        data=self.get_vendor_form()
        data['profile']=profile.pk
        response = self.client.post(url,
                                    data,
                                    follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Profile View' in response.content)

    def test_create_vendor_post_form_valid_submit(self):
        url = reverse('vendor_create', urlconf='gbe.urls')
        profile = ProfileFactory()
        login_as(profile, self)
        data=self.get_vendor_form(submit=True)
        data['profile']=profile.pk
        response = self.client.post(url,
                                    data,
                                    follow=True)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true('Vendor Payment' in response.content)

    def test_create_vendor_post_form_invalid(self):
        request = self.factory.get('vendor/bid/')
        request.method = 'POST'
        request.user = ProfileFactory.create().user_object
        request.POST = self.get_vendor_form(invalid=True)
        request.session = {'cms_admin_site':1}
        response = create_vendor(request)
        nt.assert_equal(response.status_code, 200)

    def test_create_vendor_no_post(self):
        request = self.factory.get('vendor/bid/')
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site':1}
        response = create_vendor(request)
        nt.assert_equal(response.status_code, 200)
