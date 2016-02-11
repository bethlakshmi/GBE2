from django.http import Http404
from django.core.exceptions import PermissionDenied
from ticketing.models import *
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.ticketing_factories import (
    TicketingEligibilityConditionFactory,
    TransactionFactory
)
from tests.factories.gbe_factories import (
    ConferenceFactory
)
from datetime import datetime
import pytz
from gbe.ticketing_idd_interface import get_checklist_items_for_tickets


class TestIsExcluded(TestCase):
    '''Tests for exclusions in all Exclusion subclasses'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.ticketingcondition = TicketingEligibilityConditionFactory.create()
        self.transaction = TransactionFactory.create()
        self.purchaser = self.transaction.purchaser
        self.conference = self.transaction.ticket_item.bpt_event.conference

    def test_no_ticket_condition(self):
        '''
            purchaser tickets have no conditions
        '''
        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference)
        nt.assert_equal(len(checklist_items), 0)

    def test_no_ticket_purchase(self):
        '''
            purchaser didn't buy anything in this conference
        '''
        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            ConferenceFactory.create())
        nt.assert_equal(len(checklist_items), 0)

    def test_no_tickets__this_conference(self):
        '''
            list of tickets is empty, so there should be no match
        '''
        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [])
        nt.assert_equal(len(checklist_items), 0)

    def test_ticket_match_happens(self):
        '''
            feeding in the matching ticket, gives an item
        '''
        match_condition = TicketingEligibilityConditionFactory.create(
            tickets=[self.transaction.ticket_item])

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [self.transaction.ticket_item])
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 1)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem])

    def test_ticket_match_happens(self):
        '''
            search conditions are right to find a checklist item
        '''
        match_condition = TicketingEligibilityConditionFactory.create(
            tickets=[self.transaction.ticket_item])

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference)
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 1)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem])

    def test_multiple_ticket_match_happens(self):
        '''
            feeding in the matching ticket, gives an item
        '''
        match_condition = TicketingEligibilityConditionFactory.create(
            tickets=[self.transaction.ticket_item])
        another_transaction = TransactionFactory.create(
            purchaser=self.purchaser,
            ticket_item=self.transaction.ticket_item)

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [self.transaction.ticket_item, another_transaction.ticket_item])
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 2)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem])

    def test_ticket_multiple_match_happens(self):
        '''
            purchaser has 2 of same ticket
        '''
        match_condition = TicketingEligibilityConditionFactory.create(
            tickets=[self.transaction.ticket_item])
        another_transaction = TransactionFactory.create(
            purchaser=self.purchaser,
            ticket_item=self.transaction.ticket_item)

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference)
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 2)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem])

    def test_ticket_match_two_conditions(self):
        '''
            two conditions match this circumstance
        '''
        match_condition = TicketingEligibilityConditionFactory.create(
            tickets=[self.transaction.ticket_item])
        another_match = TicketingEligibilityConditionFactory.create(
            tickets=[self.transaction.ticket_item])

        checklist_items = get_checklist_items_for_tickets(
            self.purchaser,
            self.conference,
            [self.transaction.ticket_item])
        nt.assert_equal(len(checklist_items), 1)
        nt.assert_equal(checklist_items[0]['count'], 1)
        nt.assert_equal(checklist_items[0]['ticket'],
                        self.transaction.ticket_item.title)
        nt.assert_equal(checklist_items[0]['items'],
                        [match_condition.checklistitem,
                         another_match.checklistitem])
