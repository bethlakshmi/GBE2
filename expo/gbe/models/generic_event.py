
from itertools import chain
from django.db.models import (
    CharField,
    ForeignKey,
)

from event import Event
from available_interest import AvailableInterest
from gbetext import event_options


class GenericEvent (Event):
    '''
    Any event except for a show or a class
    '''
    type = CharField(max_length=128,
                     choices=event_options,
                     blank=False,
                     default="Special")
    volunteer_type = ForeignKey(AvailableInterest,
                                blank=True,
                                null=True)

    def __str__(self):
        return self.title

    @property
    def volunteer_category_description(self):
        if self.volunteer_type:
            return self.volunteer_type.interest
        else:
            return ''

    @property
    def sched_payload(self):
        types = dict(event_options)
        payload = {
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'details': {'type': types[self.type]},
        }
        if self.parent_event:
            payload['details']['parent_event'] = self.parent_event.detail_link
            if self.volunteer_type:
                payload[
                    'details'][
                    'volunteer_category'] = self.volunteer_category_description
        return payload

    @property
    def parent_event(self):
        if self.type != 'Volunteer':
            return None
        sevent = self.eventitem_ptr.scheduler_events.first()
        from scheduler.models import EventContainer
        query = EventContainer.objects.filter(child_event=sevent)
        if query.count() == 0:
            return None
        parent = query.first().parent_event
        return parent

    @property
    def schedule_ready(self):
        return True

    # tickets that apply to generic events are:
    #   - any ticket that applies to "most" iff this is not a master class
    #   - any ticket that links this event specifically
    # but for all tickets - iff the ticket is active
    #
    def get_tickets(self):
        from ticketing.models import TicketItem
        if self.type in ["Special", "Drop-In"]:
            most_events = TicketItem.objects.filter(
                bpt_event__include_most=True,
                active=True,
                bpt_event__conference=self.conference)
        else:
            most_events = []
        my_events = TicketItem.objects.filter(bpt_event__linked_events=self,
                                              active=True)
        tickets = list(chain(my_events, most_events))
        return tickets

    class Meta:
        app_label = "gbe"
