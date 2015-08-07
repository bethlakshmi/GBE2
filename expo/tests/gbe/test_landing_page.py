import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from gbe.views import landing_page
from tests.factories import gbe_factories as factories


class TestIndex(TestCase):
    '''Tests for index view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.profile_factory = factories.ProfileFactory

    def test_landing_page_path(self):
        '''Basic test of landing_page view
        '''
        profile = self.profile_factory.create()
        request = self.factory.get('/')
        request.user = profile.user_object
        response = landing_page(request)
        self.assertEqual(response.status_code, 200)
