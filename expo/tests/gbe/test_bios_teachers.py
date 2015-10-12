from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import bios_teachers
from tests.factories import gbe_factories as factories


class TestReviewProposalList(TestCase):
    '''Tests for bios_teachers view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_bios_teachers_authorized_user(self):
        proposal = factories.ClassProposalFactory.create()
        request = self.factory.get('bios/teachers/')
        request.user = factories.ProfileFactory.create().user_object
        request.session = {'cms_admin_site':1}
        response = bios_teachers(request)
        nt.assert_equal(response.status_code, 200)
