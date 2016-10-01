from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory
)

from ticketing.models import (
    BrownPaperEvents,
    BrownPaperSettings,
    TicketItem,
    Transaction
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    BrownPaperSettingsFactory,
    TicketItemFactory,
    TransactionFactory,
)


class PurchaseTicketContext:

    def __init__(self, profile=None, conference=None, event=None, ticket=None):
        self.transaction = TransactionFactory()
        self.transaction.ticket_item.bpt_event.badgeable = True
        self.transaction.save()
        self.transaction.ticket_item.bpt_event.save()
        self.profile.user_object = transaction.purchaser.matched_to_user
        self.profile.save()
