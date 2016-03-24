import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import publish_proposal
from tests.factories.gbe_factories import (
    ClassProposalFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestPublishProposal(TestCase):
    '''Tests for publish_proposal view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_publish_proposal_not_post(self):
        proposal = ClassProposalFactory()
        request = self.factory.get('classpropose/edit/%d' % proposal.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = publish_proposal(request, proposal.pk)
        nt.assert_equal(response.status_code, 200)

    def test_publish_proposal_post_invalid_form(self):
        proposal = ClassProposalFactory()
        request = self.factory.post('classpropose/edit/%d' % proposal.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        response = publish_proposal(request,  proposal.pk)
        nt.assert_equal(response.status_code, 200)

    def test_publish_proposal_post_valid_form(self):
        proposal = ClassProposalFactory()
        request = self.factory.post('classpropose/edit/%d' % proposal.pk)
        request.user = self.privileged_user
        request.session = {'cms_admin_site': 1}
        request.POST = self.get_class_form()
        response = publish_proposal(request, proposal.pk)
        nt.assert_equal(response.status_code, 200)
