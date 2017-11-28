from model_utils.managers import InheritanceManager
from django.db.models import (
    CharField,
    TextField,
    AutoField,
    ForeignKey,
)

from gbe.expomodelfields import DurationField
from scheduler.models import EventItem
from scheduler.idd import (
    get_occurrences,
    get_bookings,
)
from gbe.models import (
    Conference,
    Room
)
from gbetext import calendar_for_event


class Event(EventItem):
    '''
    Event is the base class for any scheduled happening at the expo.
    Events fall broadly into "shows" and "classes". Classes break down
    further into master classes, panels, workshops, etc. Shows are not
    biddable (though the Acts comprising them are) , but classes arise
    from participant bids.
    '''
    objects = InheritanceManager()
    e_title = CharField(max_length=128)
    e_description = TextField()            # public-facing description
    blurb = TextField(blank=True)        # short description
    duration = DurationField()
    notes = TextField(blank=True)  # internal notes about this event
    event_id = AutoField(primary_key=True)
    e_conference = ForeignKey(
        Conference,
        related_name="e_conference_set",
        blank=True,
        null=True)
    default_location = ForeignKey(Room,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return self.e_title

    @classmethod
    def get_all_events(cls, conference):
        events = cls.objects.filter(
            e_conference=conference,
            visible=True).select_subclasses()
        return [event for event in events if
                getattr(event, 'accepted', 3) == 3 and
                getattr(event, 'type', 'X') not in ('Volunteer',
                                                    'Rehearsal Slot',
                                                    'Staff Area')]

    @property
    def interested(self):
        interested = []
        occurrence_ids = []
        occurrence_resp = get_occurrences(foreign_event_ids=[self.eventitem_id])
        for occurrence in occurrence_resp.occurrences:
            occurrence_ids += [occurrence.pk]
        if len(occurrence_ids) > 0:
            interested_resp = get_bookings(occurrence_ids,
                                           role="Interested")
            interested = interested_resp.people
        return interested

    @property
    def sched_payload(self):
        return {'title': self.e_title,
                'description': self.e_description,
                'duration': self.duration,
                'details': {'type': ''}
                }

    @property
    def event_type(self):
        return self.__class__.__name__

    @property
    def sched_duration(self):
        return self.duration

    @property
    def bio_payload(self):
        return None

    @property
    def calendar_type(self):
        return calendar_for_event[self.__class__.__name__]

    @property
    def get_tickets(self):
        return []  # self.ticketing_item.all()

    @property
    def is_current(self):
        return self.e_conference.status == "upcoming"

    class Meta:
        ordering = ['e_title']
        app_label = "gbe"
