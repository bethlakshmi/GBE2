from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory
)
from tests.factories.ticketing_factories import (
    TransactionFactory,
)


class PurchasedTicketContext:

    def __init__(self, profile=None, conference=None, bpt_event=None,
                 ticket=None):
        self.transaction = TransactionFactory(
            ticket_item__bpt_event__badgeable=True
        )
        self.profile = ProfileFactory(
            user_object = self.transaction.purchaser.matched_to_user
        )
