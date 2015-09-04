from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import conference_volunteer
import mock
from django.contrib.auth.models import Group
import gbe.ticketing_idd_interface 
from tests.factories import gbe_factories as factories
from tests.functions.gbe_functions import (login_as,
                                           is_login_page,
                                           is_profile_update_page,
                                           location)


class TestReviewProposalList(TestCase):
    '''Tests for conference_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = factories.PersonaFactory.create()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_conference_volunteer_authorized_user(self):
        proposal = factories.ClassProposalFactory.create()
        request = self.factory.get('classpropose/reviewlist/')
        request.user = factories.ProfileFactory.create().user_object
        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 200)
