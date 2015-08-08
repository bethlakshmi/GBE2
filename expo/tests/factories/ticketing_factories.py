import factory
from factory import DjangoModelFactory
from factory import SubFactory
import ticketing.models as tickets
import gbe.models as conf
from tests.factories import gbe_factories


class BrownPaperEventsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.BrownPaperEvents
    bpt_event_id = "111111"
    conference = SubFactory(gbe_factories.ConferenceFactory)

class TicketItemFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketItem
    bpt_event = SubFactory(BrownPaperEventsFactory)
    ticket_id = "111111-222222"
    title = "Test Ticket Item"
    description = "Describing Test Ticket Item"
    cost = 99.99
    modified_by = "Ticket Item Mock"