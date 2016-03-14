import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import bid_changestate
from tests.factories.gbe_factories import (
    ActFactory,
    PersonaFactory,
    ProfileFactory,
)


class TestReviewProposalList(TestCase):
    '''Tests for bid_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()

    def test_bid_changestate_authorized_user(self):
        act = ActFactory()
        request = self.factory.get('act/changestate/%d' % act.pk)
        request.user = ProfileFactory().user_object
        response = bid_changestate(request, act.pk, 'act_review_list')
        nt.assert_equal(response.status_code, 302)
