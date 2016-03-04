from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import conference_volunteer
from tests.factories.gbe_factories import (
    ClassFactory,
    ClassProposalFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)


class TestConferenceVolunteer(TestCase):
    '''Tests for conference_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_conference_volunteer_authorized_user(self):
        proposal = ClassProposalFactory()
        request = self.factory.get('conference/volunteer/')
        request.user = ProfileFactory().user_object
        request.session = {'cms_admin_site': 1}
        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 200)



    def test_conference_volunteer_no_persona(self):
        proposal = ClassProposalFactory(display=True)
        request = self.factory.get('conference/volunteer/')
        request.user = UserFactory()
        request.session = {'cms_admin_site': 1}
        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 302)




    # def test_conference_volunteer_no_personae(self):
    #     '''class_bid, when profile has no personae,
    #     should redirect to persona_create'''
    #     profile = ProfileFactory()
    #     request = self.factory.get('conference/volunteer/')
    #     request.user = profile.user_object
    #     request.session = {'cms_admin_site': 1}
    #     response = conference_volunteer(request)
    #     nt.assert_equal(response.status_code, 302)
