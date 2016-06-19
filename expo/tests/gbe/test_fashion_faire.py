from gbe.models import (
    Conference,
)
import nose.tools as nt
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    VendorFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import login_as
from unittest import skip

class TestReviewProposalList(TestCase):
    '''Tests for fashion_faire view'''
    view_name = 'fashion_faire'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_fashion_faire_authorized_user(self):
        proposal = VendorFactory()
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)

    @skip
    def test_filter_by_conference(self):
        Conference.objects.all().delete()
        conference = ConferenceFactory(status='upcoming')
        otherconf = ConferenceFactory()
        proposal = VendorFactory(b_conference=conference,
                                 accepted=3)

        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url,
                                   data={'conference': conference})
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(proposal.b_title in response.content)

    @skip
    def test_filter_by_conference_default(self):
        Conference.objects.all().delete()
        conference = ConferenceFactory()
        conference.status = 'upcoming'
        conference.save()
        otherconf = ConferenceFactory()
        proposal = VendorFactory(b_conference=conference,
                                 accepted=3)
        url = reverse(self.view_name,
                      urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        nt.assert_equal(response.status_code, 200)
        nt.assert_true(proposal.b_title in response.content)
