from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    PersonaFactory,
    RoomFactory,

    TransactionFactory,
    ProfileFactory
)



class PurchaseTicketContext:

    def __init__():
        pass


    def create_transaction(self):
        transaction = TransactionFactory()
        transaction.ticket_item.bpt_event.badgeable = True
        transaction.save()
        transaction.ticket_item.bpt_event.save()
        profile_buyer = ProfileFactory()
        profile_buyer.user_object = transaction.purchaser.matched_to_user
        profile_buyer.save()

        return transaction
