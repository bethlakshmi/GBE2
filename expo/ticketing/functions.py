from ticketing.models import TicketItem
from itertools import chain

def get_tickets(linked_event, most=False, conference=False):
    general_events = []
    unique_tickets = {}

    if most:
        general_events = TicketItem.objects.filter(
            bpt_event__include_most=True,
            bpt_event__conference=linked_event.conference)
    if conference:
        general_events = list(chain(
            general_events,
            TicketItem.objects.filter(
                bpt_event__include_conference=True,
                bpt_event__conference=linked_event.conference)))

    general_events = list(chain(
        general_events,
        TicketItem.objects.filter(
            bpt_event__linked_events=linked_event)))
        
    for ticket_item in general_events:
        if ticket_item.active and (
                ticket_item.bpt_event.bpt_event_id not in unique_tickets or \
                ticket_item.cost > unique_tickets[
                    ticket_item.bpt_event.bpt_event_id].cost): 
            unique_tickets[ticket_item.bpt_event.bpt_event_id] = ticket_item

    return unique_tickets
