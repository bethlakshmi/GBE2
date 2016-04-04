import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfileFactory,
    ProfilePreferencesFactory,
    UserFactory,
)
from tests.functions.gbe_functions import login_as


class TestUpdateProfile(TestCase):
    '''Tests for update_profile  view'''
    view_name='profile_update'

    def setUp(self):
        self.client = Client()
        self.counter = 0

    def get_form(self, invalid=False):
        self.counter +=1
        email = "new%d@last.com" % self.counter
        data = {'first_name': 'new first',
                'last_name': 'new last',
                'display_name': 'Display P. Name',
                'email': email,
                'purchase_email': email,
                'address1': '789 Elm St',
                'address2': 'Apt. e',
                'city': 'Konigsburg',
                'state': 'PA',
                'zip_code': '23456',
                'country': 'USA',
                'phone': '617-555-2121',
                'best_time': 'Any',
                'how_heard': 'Facebook',
                'prefs-inform_about': 'Performing',
                'in_hotel': True,
                'show_hotel_infobox': False}
        if invalid:
            del(data['first_name'])
        return data

    def test_update_profile_no_such_profile(self):
        user = UserFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        nt.assert_true(user.profile is not None)

    def test_update_profile_post_valid_form(self):
        profile = ProfilePreferencesFactory().profile

        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        data = self.get_form()
        response = self.client.post(url, data=data, follow=True)
        nt.assert_true("Your Account" in response.content)
        nt.assert_true(('http://testserver/gbe', 302) in response.redirect_chain)


    def test_update_profile_post_invalid_form(self):
        profile = ProfilePreferencesFactory().profile

        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        data = self.get_form(invalid=True)
        response = self.client.post(url, data=data, follow=True)
        nt.assert_true("Update Profile" in response.content)
        nt.assert_equal(response.status_code, 200)
