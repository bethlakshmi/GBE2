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
    ConferenceVolunteerFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from gbe.models import ClassProposal
from gbetext import conf_volunteer_save_error


class TestConferenceVolunteer(TestCase):
    '''Tests for conference_volunteer view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description',
                'presenter': 1,
                'bid': 1,
                'how_volunteer': 1
                }

    def test_conference_volunteer_no_visible_class_proposals(self):
        ClassProposal.objects.all().delete()
        proposal = ClassProposalFactory(display=False)
        request = self.factory.get('conference/volunteer/')
        request.user = ProfileFactory().user_object
        request.session = {'cms_admin_site': 1}
        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 200)

    def test_conference_volunteer_no_profile(self):
        ClassProposal.objects.all().delete()
        proposal = ClassProposalFactory(display=False)
        request = self.factory.get('conference/volunteer/')
        request.user = UserFactory()
        request.session = {'cms_admin_site': 1}
        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 302)

    def test_conference_volunteer_post_offer_form_invalid(self):
        proposal = ClassProposalFactory(display=True)
        persona = PersonaFactory()
        data = self.get_class_form()
        data["%d-volunteering" % proposal.id] = 1
        request = self.factory.post('conference/volunteer/',
                                    data=data)

        request.user = persona.contact.user_object
        request.session = {'cms_admin_site': 1}
        response = conference_volunteer(request)

        nt.assert_equal(response.status_code, 200)
        nt.assert_true(conf_volunteer_save_error in response.content)

    def test_conference_volunteer_post_offer_form_valid(self):
        proposal = ClassProposalFactory(display=True)
        persona = PersonaFactory()
        data = self.get_class_form()
        data["%d-volunteering" % proposal.id] = 1
        data["%d-bid" % proposal.pk] = proposal.id
        data['%d-how_volunteer' % proposal.pk] = 'Any of the Above'
        data['%d-presenter' % proposal.pk] = persona.pk
        request = self.factory.post('conference/volunteer/',
                                    data=data)
        request.user = persona.contact.user_object
        request.session = {'cms_admin_site': 1}

        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 302)

    def test_conference_volunteer_post_offer_existing_volunteer(self):
        proposal = ClassProposalFactory(display=True)
        persona = ConferenceVolunteerFactory(
            bid=proposal).presenter

        data = self.get_class_form()
        data["%d-volunteering" % proposal.id] = 1
        data["%d-bid" % proposal.pk] = proposal.id
        data['%d-how_volunteer' % proposal.pk] = 'Any of the Above'
        data['%d-presenter' % proposal.pk] = persona.pk
        request = self.factory.post('conference/volunteer/',
                                    data=data)
        request.user = persona.contact.user_object
        request.session = {'cms_admin_site': 1}
        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 302)

    def test_conference_volunteer_get(self):
        proposal = ClassProposalFactory(display=True)
        ClassProposalFactory(display=True,
                             type="Panel")
        ClassProposalFactory(display=True,
                             type="Shoe")
        persona = ConferenceVolunteerFactory(
            bid=proposal).presenter

        request = self.factory.get('conference/volunteer/')
        request.user = persona.contact.user_object
        request.session = {'cms_admin_site': 1}

        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 200)

    def test_conference_volunteer_no_persona(self):
        proposal = ClassProposalFactory(display=True)
        request = self.factory.get('conference/volunteer/')
        request.user = ProfileFactory().user_object
        request.session = {'cms_admin_site': 1}
        response = conference_volunteer(request)
        nt.assert_equal(response.status_code, 302)
