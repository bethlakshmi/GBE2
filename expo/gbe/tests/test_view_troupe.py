import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_troupe
import factories


class TestViewTroupe(TestCase):
    '''Tests for view_troupe view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.troupe_string = 'Tell Us About Your Troupe'

    def test_view_troupe(self):
        '''view_troupe view, success
        '''
        persona = factories.PersonaFactory.create()
        contact = persona.performer_profile
        troupe = factories.TroupeFactory.create(contact=contact)
        request = self.factory.get('/troupe/view/%d' % troupe.resourceitem_id)
        request.user = contact.profile.user_object
        response = view_troupe(request, troupe.resourceitem_id)
        self.assertEqual(response.status_code, 200)
