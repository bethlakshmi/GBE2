import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import view_costume
from tests.factories.gbe_factories import CostumeFactory


class TestViewCostume(TestCase):
    '''Tests for view_costume view'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_view_costume(self):
        '''view_costume view, success
        '''
        costume = CostumeFactory()
        request = self.factory.get('/costume/view/%d' % costume.pk)
        request.user = costume.profile.user_object
        request.session = {'cms_admin_site': 1}
        response = view_costume(request, costume.pk)
        self.assertEqual(response.status_code, 200)
