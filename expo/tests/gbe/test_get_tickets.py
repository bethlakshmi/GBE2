import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.models import GenericEvent, Show, Class
from ticketing.models import TicketItem
import mock


class TestGetTickets(TestCase):
    '''Tests for edit_event view'''

    # Fixture to create some rooms, location items, and resource items
    fixtures = ['expo/tests/fixtures/tickets_to_events.json']

    def test_get_tickets_for_volunteer_opp(self):
        '''should get no tickets, volunteer opportunities are free
        '''
        event = GenericEvent.objects.get(pk=12)
        tickets = event.get_tickets()

        self.assertEqual(tickets, [])

    def test_get_tickets_for_master_class(self):
        '''get the one ticket that is active for the Master Class
        '''
        event = GenericEvent.objects.get(pk=4)
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].title, "Master Class 2017")

    def test_get_tickets_for_special_event(self):
        '''get the one ticket that is active for all except master classes
        '''
        event = GenericEvent.objects.get(pk=8)
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].title, "The Whole Shebang 2016")

    def test_get_tickets_for_class(self):
        '''get one ticket for everything but master, and one for classes
        '''
        event = Class.objects.get(pk=2)
        tickets = event.get_tickets()

        whole_shebang = TicketItem.objects.get(pk=1)
        scholar = TicketItem.objects.get(pk=3)

        self.assertEqual(len(tickets), 2)
        self.assertIn(whole_shebang, tickets)
        self.assertIn(scholar, tickets)

    def test_get_tickets_for_show(self):
        '''just gets 1 ticket for Whole Shebang
        '''
        event = Show.objects.get(pk=2)
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].title, "The Whole Shebang 2016")
