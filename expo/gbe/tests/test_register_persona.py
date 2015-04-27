import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from gbe.views import register_persona
import factories


class TestRegisterPersona(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.user_factory = factories.UserFactory

    def test_register_persona(self):
        '''Basic test of register_persona view
        '''
        request = self.factory.get('/')
        request.user = self.user_factory.create()
        request.method = 'POST'
        response = register_persona(request)
        self.assertEqual(response.status_code, 302)  # why 302?
