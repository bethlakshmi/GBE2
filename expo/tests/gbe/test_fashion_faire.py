from django.shortcuts import get_object_or_404
from django.http import Http404
from gbe.models import (
    Conference,
)
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import fashion_faire
from django.contrib.auth.models import Group
from tests.factories.gbe_factories import (
    VendorFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)


class TestReviewProposalList(TestCase):
    '''Tests for fashion_faire view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_fashion_faire_authorized_user(self):
        proposal = VendorFactory.create()
        request = self.factory.get('fashion_faire')
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}
        response = fashion_faire(request)
        nt.assert_equal(response.status_code, 200)

    def test_filter_by_conference(self):
        proposal = VendorFactory.create()
        Conference.objects.all().delete()
        conference = ConferenceFactory.create()
        conference.status = 'upcoming'
        conference.save()
        otherconf = ConferenceFactory.create()
        proposal.conference = conference
        proposal.title = "some vendor"
        proposal.accepted = 3
        proposal.save()
        request = self.factory.get('fashion_faire',
                                   data={'conference': conference})
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}

        response = fashion_faire(request)

        nt.assert_true(proposal.title in response.content)

    def test_filter_by_conference_default(self):
        proposal = VendorFactory.create()
        Conference.objects.all().delete()
        conference = ConferenceFactory.create()
        conference.status = 'upcoming'
        conference.save()
        otherconf = ConferenceFactory.create()
        proposal.conference = conference
        proposal.title = "some vendor"
        proposal.accepted = 3
        proposal.save()
        request = self.factory.get('fashion_faire')
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}

        response = fashion_faire(request)

        nt.assert_true(proposal.title in response.content)
