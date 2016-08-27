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

        self.assertEqual(tickets, [])

    def test_get_tickets_for_master_class(self):
        '''get the one ticket that is active for the Master Class
        '''
        event = GenericEventFactory(
            type='Master')
        bpt_event = BrownPaperEventsFactory(conference=event.conference)
        bpt_event.linked_events.add(event)
        bpt_event.save()
        TicketItemFactory(bpt_event=bpt_event,
                          active=True,
                          title="Master Class 2017")
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].title, "Master Class 2017")

    def test_get_tickets_for_special_event(self):
        '''get the one ticket that is active for all except master classes
        '''
        event = GenericEventFactory(
            type='Special')
        bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_most=True)
        TicketItemFactory(bpt_event=bpt_event,
                          active=True,
                          title="The Whole Shebang 2016")

        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].title, "The Whole Shebang 2016")

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
            active=True,
            title="The Whole Shebang 2016")
        scholar = TicketItemFactory(
            bpt_event=sch_bpt_event,
            active=True,
            title="The Scholar 2016")
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 2)
        self.assertIn(whole_shebang, tickets)
        self.assertIn(scholar, tickets)

    def test_get_tickets_for_show(self):
        '''just gets 1 ticket for Whole Shebang
        '''
        event = ShowFactory()
        bpt_event = BrownPaperEventsFactory(
            conference=event.conference,
            include_most=True)
        TicketItemFactory(bpt_event=bpt_event,
                          active=True,
                          title="The Whole Shebang 2016")
        tickets = event.get_tickets()

        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].title, "The Whole Shebang 2016")
