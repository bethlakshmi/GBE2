import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_troupe
import factories
from functions import (
    login_as,
    location,
    )


class TestEditTroupe(TestCase):
    '''Tests for edit_troupe view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_create_troupe(self):
        '''edit_troupe view, create flow
        '''
        contact = factories.PersonaFactory.create()
        request = self.factory.get('/troupe/create/')
        request.user = factories.UserFactory.create()
        response = edit_troupe(request)
        self.assertEqual(response.status_code, 302)

        user = factories.UserFactory.create()
        login_as(user, self)
        request.user = user
        response = edit_troupe(request)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response),
                        '/update_profile?next=/troupe/create')
        request.user = contact.performer_profile.user_object
        login_as(contact.performer_profile, self)
        response = edit_troupe(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.troupe_string in response.content)

    def test_edit_troupe(self):
        '''edit_troupe view, edit flow success
        '''
        persona = factories.PersonaFactory.create()
        contact = persona.performer_profile
        troupe = factories.TroupeFactory.create(contact=contact)
        request = self.factory.get('/troupe/edit/%d' % troupe.pk)
        request.user = contact.profile.user_object
        self.client.logout()
        response = edit_troupe(request)
        self.assertEqual(response.status_code, 200)
