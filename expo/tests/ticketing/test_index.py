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

    def test_one_ticket(self):
        '''
           user gets the list
        '''
        ticket = TicketItemFactory(live=True)
        request = self.factory.get(
            reverse('index', urlconf='ticketing.urls'),
        )
        request.user = UserFactory()
        request.session = {'cms_admin_site': 1}
        response = index(request)
        assert ticket.title in response.content

    def test_no_ticket(self):
        '''
           user gets the list
        '''
        request = self.factory.get(
            reverse('index', urlconf='ticketing.urls'),
        )
        request.user = UserFactory()
        response = index(request)
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
        request = self.factory.get(
            reverse('index', urlconf='ticketing.urls'),
        )
        request.user = UserFactory()
        request.session = {'cms_admin_site': 1}
        response = index(request)
        assert ticket.title in response.content
        assert not_shown.title not in response.content
