import factory
from factory import DjangoModelFactory
from factory import SubFactory
import ticketing.models as tickets
import gbe.models as conf
from tests.factories import gbe_factories
from django.utils import timezone


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


class PurchaserFactory(DjangoModelFactory):
    class Meta:
        model = tickets.Purchaser
    first_name = "Betty"
    last_name = "Blaize"
    address = "12 Betty Lane"
    city = "Boston"
    state = "MA"
    zip = "12312"
    country = "USA"
    email = "purchaseemail@test.com"
    phone = "111-222-3333"
    matched_to_user = SubFactory(gbe_factories.UserFactory)


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.Transaction
    ticket_item = SubFactory(TicketItemFactory)
    purchaser = SubFactory(PurchaserFactory)
    amount = 99.99
    order_date = timezone.now()
    shipping_method = ""
    order_notes = ""
    reference = ""
    payment_source = ""
