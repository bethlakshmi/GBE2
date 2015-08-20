import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import create_combo
import factories
from functions import (
    login_as,
    location,
)


class TestCreateCombo(TestCase):
    '''Tests for create_combo view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'a one-off group of performers working together'

    def test_create_troupe(self):
        '''edit_troupe view, create flow
        '''
        contact = factories.PersonaFactory.create()
        request = self.factory.get('/combo/create/')
        request.user = factories.UserFactory.create()
        response = create_combo(request)
        self.assertEqual(response.status_code, 302)
        user = factories.UserFactory.create()
        login_as(user, self)
        request.user = user
        response = create_combo(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response),
                        '/update_profile?next=/troupe/create')
        request.user = contact.performer_profile.user_object
        login_as(contact.performer_profile, self)
        response = create_combo(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.troupe_string in response.content)
