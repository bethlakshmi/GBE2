import nose.tools as nt
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
import mock
from tests.factories.gbe_factories import (
    ClassFactory,
    GenericEventFactory,
    ShowFactory
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    TicketItemFactory
)


class TestGetTickets(TestCase):
    '''Tests for edit_event view'''

    # Fixture to create some rooms, location items, and resource items

    def test_get_tickets_for_volunteer_opp(self):
        '''should get no tickets, volunteer opportunities are free
        '''
        event = GenericEventFactory()
        tickets = event.get_tickets()

        self.assertEqual(tickets, {})

    def test_get_tickets_for_master_class(self):
        '''get the one ticket that is active for the Master Class
        '''
        event = GenericEventFactory(
            type='Master')
        bpt_event = BrownPaperEventsFactory(conference=event.conference)
        bpt_event.linked_events.add(event)
        bpt_event.save()
        TicketItemFactory(bpt_event=bpt_event,
                          live=True,
                          has_coupon=False,
                          title="Master Class 2017")
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[bpt_event.bpt_event_id].title,
            "Master Class 2017")

    def test_get_tickets_for_special_event(self):
        '''get the one ticket that is active for all except master classes
        '''
        event = GenericEventFactory(
            type='Special')
        bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_most=True)
        TicketItemFactory(bpt_event=bpt_event,
                          live=True,
                          has_coupon=False,
                          title="The Whole Shebang 2016")

        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[bpt_event.bpt_event_id].title,
            "The Whole Shebang 2016")

    def test_get_tickets_for_class(self):
        '''get one ticket for everything but master, and one for classes
        '''
        event = ClassFactory()
        ws_bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_most=True)
        sch_bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_conference=True)
        whole_shebang = TicketItemFactory(
            bpt_event=ws_bpt_event,
            live=True,
            has_coupon=False,
            title="The Whole Shebang 2016")
        scholar = TicketItemFactory(
            bpt_event=sch_bpt_event,
            live=True,
            has_coupon=False,
            title="The Scholar 2016")
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 2)
        self.assertEqual(
            tickets[ws_bpt_event.bpt_event_id],
            whole_shebang)
        self.assertEqual(
            tickets[sch_bpt_event.bpt_event_id],
            scholar)

    def test_get_tickets_for_show(self):
        '''just gets 1 ticket for Whole Shebang
        '''
        event = ShowFactory()
        bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_most=True)
        TicketItemFactory(bpt_event=bpt_event,
                          live=True,
                          has_coupon=False,
                          title="The Whole Shebang 2016")
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[bpt_event.bpt_event_id].title,
            "The Whole Shebang 2016")

    def test_get_tickets_for_class_three_ways(self):
        '''the ticket is linked to the class event three ways - 'most',
        'conference', and a direct link.  It only should appear once.
        '''
        event = ClassFactory()
        bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_most=True,
            include_conference=True)
        bpt_event.linked_events.add(event)
        bpt_event.save()
        TicketItemFactory(bpt_event=bpt_event,
                          live=True,
                          has_coupon=False,
                          title="The Whole Shebang 2016")

        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(
            tickets[bpt_event.bpt_event_id].title,
            "The Whole Shebang 2016")

    def test_get_tickets_nothing_active(self):
        '''the ticket is linked to the class and there are two active prices
        only the most expensive is shown
        '''
        event = ClassFactory()
        bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_conference=True)
        TicketItemFactory(bpt_event=bpt_event,
                          live=False,
                          has_coupon=False,
                          title="The Whole Shebang 2016")
        TicketItemFactory(bpt_event=bpt_event,
                          live=True,
                          has_coupon=True,
                          cost=299.99,
                          title="The Whole Shebang 2016 - expensive")

        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 0)
