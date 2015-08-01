import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import edit_persona
import factories
from functions import (login_as,
                       is_login_page,
                       is_profile_update_page,
                       location)

class TestEditPersona(TestCase):
    '''Tests for edit_persona view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Stage Persona'

    def test_edit_persona(self):
        '''edit_troupe view, create flow
        '''
        contact = factories.PersonaFactory.create()
        request = self.factory.get('/persona/edit/%d'%contact.resourceitem_id)
        request.user = factories.UserFactory.create()
        response = edit_persona(request, contact.resourceitem_id)
        nt.assert_equal(response.status_code, 302)
        


        user = factories.UserFactory.create()
        login_as(user, self)
        request.user = user
        response = edit_persona(request, contact.resourceitem_id)
        nt.assert_equal(response.status_code, 302)
        nt.assert_equal(location(response), 
                        '/profile')
        request.user = contact.performer_profile.user_object
        login_as(contact.performer_profile, self)
        response = edit_persona(request, contact.resourceitem_id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.troupe_string in response.content)


