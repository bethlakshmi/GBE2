from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ProfilePreferencesFactory,
    UserFactory,
    UserMessageFactory
)
from gbe.models import UserMessage
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as
)
from gbetext import default_update_profile_msg
from unittest import skip

class TestUpdateProfile(TestCase):
    '''Tests for update_profile  view'''
    view_name = 'profile_update'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.counter = 0

    def get_form(self, invalid=False):
        self.counter += 1
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

    def post_profile(self):
        profile = ProfilePreferencesFactory().profile

        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        data = self.get_form()
        response = self.client.post(url, data=data, follow=True)
        return response

    def test_update_profile_no_such_profile(self):
        user = UserFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(user, self)
        response = self.client.get(url)
        self.assertTrue(user.profile is not None)

    @skip
    def test_update_profile_post_valid_form(self):
        response = self.post_profile()
        self.assertTrue("Your Account" in response.content)
        self.assertTrue(('http://testserver/gbe', 302)
                        in response.redirect_chain)
    @skip
    def test_update_profile_post_invalid_form(self):
        profile = ProfilePreferencesFactory().profile

        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        data = self.get_form(invalid=True)
        response = self.client.post(url, data=data, follow=True)
        self.assertTrue("Update Profile" in response.content)
        self.assertEqual(response.status_code, 200)

    def test_update_profile_make_message(self):
        response = self.post_profile()
        assert_alert_exists(
            response, 'success', 'Success', default_update_profile_msg)

    def test_update_profile_has_message(self):
        msg = UserMessageFactory(
            view='UpdateProfileView',
            code='UPDATE_PROFILE')
        response = self.post_profile()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
