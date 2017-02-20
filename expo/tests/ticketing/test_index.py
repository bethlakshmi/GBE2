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
        self.url = reverse('index', urlconf='ticketing.urls')

    def test_one_ticket(self):
        '''
           user gets the list
        '''
        ticket = TicketItemFactory(live=True)
        response = self.client.get(self.url)
        assert ticket.title in response.content

    def test_no_ticket(self):
        '''
           user gets the list
        '''
        response = self.client.get(self.url)
        nt.assert_equal(response.status_code, 200)

    def test_one_ticket_per_event(self):
        '''
           user gets the list
        '''
        not_shown = TicketItemFactory(
            live=True,
            cost=1.00,
            title='Do Not Show Me')
        ticket = TicketItemFactory(live=True,
                                   bpt_event=not_shown.bpt_event)
        response = self.client.get(self.url)
        assert ticket.title in response.content
        assert not_shown.title not in response.content
