from tests.factories.ticketing_factories import (
    TicketItemFactory
)
import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import (
    index
)
from tests.factories.gbe_factories import (
    UserFactory
)
from django.core.urlresolvers import reverse


class TestTicketingIndex(TestCase):
    '''Tests for ticketing index'''
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()

    def test_index(self):
        '''
           user gets the list
        '''
        ticket = TicketItemFactory()
        request = self.factory.get(
            reverse('index', urlconf='ticketing.urls'),
        )
        request.user = UserFactory()
        response = index(request)
        nt.assert_equal(response.status_code, 200)
