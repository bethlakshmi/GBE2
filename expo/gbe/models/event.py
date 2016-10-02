from model_utils.managers import InheritanceManager
from django.db.models import (
    CharField,
    TextField,
    AutoField,
    ForeignKey,
)

from gbe.expomodelfields import DurationField
from scheduler.models import EventItem
from remains import Conference
from room import Room


class Event(EventItem):
    '''
    Event is the base class for any scheduled happening at the expo.
    Events fall broadly into "shows" and "classes". Classes break down
    further into master classes, panels, workshops, etc. Shows are not
    biddable (though the Acts comprising them are) , but classes arise
    from participant bids.
    '''
    objects = InheritanceManager()
    title = CharField(max_length=128)
    description = TextField()            # public-facing description
    blurb = TextField(blank=True)        # short description
    duration = DurationField()
    notes = TextField(blank=True)  # internal notes about this event
    event_id = AutoField(primary_key=True)
    conference = ForeignKey(
        Conference,
        default=lambda: Conference.objects.filter(status="upcoming").first())
    default_location = ForeignKey(Room,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return self.title

    @classmethod
    def get_all_events(cls, conference):
        events = cls.objects.filter(
            conference=conference,
            visible=True).select_subclasses()
        return [event for event in events if
                getattr(event, 'accepted', 3) == 3 and
                getattr(event, 'type', 'X') not in ('Volunteer',
                                                    'Rehearsal Slot',
                                                    'Staff Area')]

    @property
    def sched_payload(self):
        return {'title': self.title,
                'description': self.description,
                'duration': self.duration,
                'details': {'type': ''}
                }

    @property
    def sched_duration(self):
        return self.duration

    @property
    def bio_payload(self):
        return None

    @property
    def calendar_type(self):
        return calendar_types[0]

    @property
    def get_tickets(self):
        return []  # self.ticketing_item.all()

    @property
    def is_current(self):
        return self.conference.status == "upcoming"

    class Meta:
        ordering = ['title']
        app_label = "gbe"
