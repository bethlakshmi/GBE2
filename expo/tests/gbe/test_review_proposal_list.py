import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import review_proposal_list
from tests.factories.gbe_factories import (
    ClassProposalFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.core.exceptions import PermissionDenied


class TestReviewProposalList(TestCase):
    '''Tests for review_proposal_list view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_review_proposal_list_authorized_user(self):
        proposal = ClassProposalFactory()
        request = self.factory.get('classpropose/reviewlist/')
        request.session = {'cms_admin_site': 1}
        request.user = self.privileged_user
        response = review_proposal_list(request)
        nt.assert_equal(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_review_proposal_list_bad_user(self):
        proposal = ClassProposalFactory()
        request = self.factory.get('classpropose/reviewlist/')
        request.user = ProfileFactory().user_object
        request.session = {'cms_admin_site': 1}
        response = review_proposal_list(request)
        nt.assert_equal(response.status_code, 200)

    @nt.raises(PermissionDenied)
    def test_review_proposal_list_no_user(self):
        proposal = ClassProposalFactory()
        request = self.factory.get('classpropose/reviewlist/')
        request.user = UserFactory()
        request.session = {'cms_admin_site': 1}
        login_as(request.user, self)
        response = review_proposal_list(request)
        nt.assert_equal(response.status_code, 302)
