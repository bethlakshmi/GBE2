from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import fashion_faire
from django.contrib.auth.models import Group
from tests.factories import gbe_factories as factories


class TestReviewProposalList(TestCase):
    '''Tests for fashion_faire view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_fashion_faire_authorized_user(self):
        proposal = factories.ClassProposalFactory.create()
        request = self.factory.get('costume_display')
        request.user = factories.ProfileFactory.create().user_object
        request.session = {'cms_admin_site':1}
        response = fashion_faire(request)
        nt.assert_equal(response.status_code, 200)
