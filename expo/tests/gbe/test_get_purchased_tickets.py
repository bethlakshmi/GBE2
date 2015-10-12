import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.models import Conference
from ticketing.models import TicketItem
from django.contrib.auth.models import User
from gbe.ticketing_idd_interface import *

import mock


class TestGetPurchasedTickets(TestCase):
    '''Tests for edit_event view'''

    # Fixture to create some rooms, location items, and resource items
    fixtures = ['tests/fixtures/tickets_to_events.json']

    def test_no_purchases(self):
        '''should get no tickets, this person never purchased any
        '''
        elcheapo = User.objects.get(pk=3)
        ticket_set = get_purchased_tickets(elcheapo)

        self.assertEqual(ticket_set, [])

    def test_buys_each_year(self):
        '''should get current and upcoming conference tickets, including fees
        '''
        buyer = User.objects.get(pk=1)
        ticket_set = get_purchased_tickets(buyer)

        self.assertEqual(len(ticket_set), 2)
        self.assertEqual(ticket_set[0]['conference'].status, "ongoing")
        self.assertEqual(ticket_set[1]['conference'].status, "upcoming")
        self.assertEqual(len(ticket_set[0]['tickets']), 3)
        self.assertEqual(len(ticket_set[1]['tickets']), 1)
