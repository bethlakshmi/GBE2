from itertools import chain


def get_unique_tickets(general_events):
    unique_tickets = {}
    for ticket_item in general_events:
        if ticket_item.active and (
                ticket_item.bpt_event.bpt_event_id not in unique_tickets or
                ticket_item.cost > unique_tickets[
                    ticket_item.bpt_event.bpt_event_id].cost):
            unique_tickets[ticket_item.bpt_event.bpt_event_id] = ticket_item

    return unique_tickets


def get_tickets(linked_event, most=False, conference=False):
    from ticketing.models import TicketItem

    general_events = []

    if most:
        general_events = TicketItem.objects.filter(
            bpt_event__include_most=True,
            bpt_event__conference=linked_event.e_conference)
    if conference:
        general_events = list(chain(
            general_events,
            TicketItem.objects.filter(
                bpt_event__include_conference=True,
                bpt_event__conference=linked_event.e_conference)))

    general_events = list(chain(
        general_events,
        TicketItem.objects.filter(
            bpt_event__linked_events=linked_event)))

    return get_unique_tickets(general_events)
