import factory
from factory import (
    DjangoModelFactory,
    Sequence,
    SubFactory
)
import ticketing.models as tickets
import gbe.models as conf
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    UserFactory
)
from django.utils import timezone


class BrownPaperEventsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.BrownPaperEvents
    bpt_event_id = "111111"
    conference = SubFactory(ConferenceFactory)


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
    matched_to_user = SubFactory(UserFactory)


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


class CheckListItemFactory(DjangoModelFactory):
    class Meta:
        model = tickets.CheckListItem
    description = Sequence(lambda x: "Check List Item: #%d" % x)


class TicketingEligibilityConditionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketingEligibilityCondition

    checklistitem = SubFactory(CheckListItemFactory)

    @factory.post_generation
    def tickets(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            self.tickets.add(SubFactory(TicketItemFactory))
            self.tickets.add(SubFactory(TicketItemFactory))
            self.tickets.add(SubFactory(TicketItemFactory))
            return

        if extracted:
            # A list of groups were passed in, use them
            for ticket in extracted:
                self.tickets.add(ticket)


class RoleEligibilityConditionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleEligibilityCondition

    checklistitem = SubFactory(CheckListItemFactory)
    role = "Teacher"


class TicketingExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketingExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)

    @factory.post_generation
    def tickets(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            self.tickets.add(SubFactory(TicketItemFactory))
            self.tickets.add(SubFactory(TicketItemFactory))
            self.tickets.add(SubFactory(TicketItemFactory))
            return

        if extracted:
            # A list of groups were passed in, use them
            for ticket in extracted:
                self.tickets.add(ticket)
    
    
class RoleExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)
    role = "Teacher"
    event = SubFactory(ClassFactory)


class NoEventRoleExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)
    role = "Teacher"
