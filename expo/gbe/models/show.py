from itertools import chain
from django.db.models import (
    ManyToManyField,
    CharField,
)
from django.conf import settings
from event import Event
from persona import Persona
from act import Act

from gbetext import cue_options

class Show (Event):
    '''
    A Show is an Event consisting of a sequence of Acts.
    Future to do: remove acts as field of this class, do acceptance
    and scheduling through scheduler  (post 2015)
    '''
    acts = ManyToManyField(Act, related_name="appearing_in", blank=True)
    mc = ManyToManyField(Persona, related_name="mc_for", blank=True)
    cue_sheet = CharField(max_length=128,
                                 choices=cue_options,
                                 blank=False,
                                 default="Theater")
    type = "Show"

    def __str__(self):
        return self.title

    @property
    def sched_payload(self):
        return {'title': self.title,
                'description': self.description,
                'duration': self.duration,
                'details': {'type': 'Show'}
                }

    @property
    def schedule_ready(self):
        return True      # shows are always ready for scheduling

    # tickets that apply to shows are:
    #   - any ticket that applies to "most" ("most"= no Master Classes)
    #   - any ticket that links this event specifically
    # but for all tickets - iff the ticket is active
    #
    def get_tickets(self):
        from ticketing.models import TicketItem
        most_events = TicketItem.objects.filter(
            bpt_event__include_most=True,
            active=True,
            bpt_event__conference=self.conference)
        my_events = TicketItem.objects.filter(
            bpt_event__linked_events=self,
            active=True)
        tickets = list(chain(my_events, most_events))
        return tickets

    def get_acts(self):
        return self.scheduler_events.first().get_acts()

    def download_path(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            "uploads",
                            "audio",
                            "downloads",
                            ("%s_%s.tar.gz" %
                             (self.conference.conference_slug,
                              self.title.replace(" ", "_").replace("/", "_"))))
        return path

    class Meta:
        app_label = "gbe"
