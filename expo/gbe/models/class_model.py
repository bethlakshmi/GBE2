import pytz
from itertools import chain
from django.db.models import (
    CharField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    Q,
    TextField,
)
from gbe.duration import Duration
from remains import (
    Conference,
    visible_bid_query,
)
from biddable import Biddable
from event import Event
from persona import Persona
from profile import Profile

from gbetext import (
    acceptance_states,
    class_length_options,
    class_options,
    space_options,
    yesno_options,
)
from gbe_forms_text import calendar_types


class Class(Biddable, Event):
    '''
    A Class is an Event where one or a few people
    teach/instruct/guide/mediate and a number of participants
    spectate/participate.
    '''
    teacher = ForeignKey(Persona,
                         related_name='is_teaching')
    minimum_enrollment = IntegerField(blank=True, default=1)
    maximum_enrollment = IntegerField(blank=True, default=20, null=True)
    organization = CharField(max_length=128, blank=True)
    type = CharField(max_length=128,
                     choices=class_options,
                     blank=True,
                     default="Lecture")
    fee = IntegerField(blank=True, default=0, null=True)
    other_teachers = CharField(max_length=128, blank=True)
    length_minutes = IntegerField(choices=class_length_options,
                                  default=60, blank=True)
    history = TextField(blank=True)
    run_before = TextField(blank=True)
    schedule_constraints = TextField(blank=True)
    avoided_constraints = TextField(blank=True)
    space_needs = CharField(max_length=128,
                            choices=space_options,
                            blank=True,
                            default='Please Choose an Option')
    physical_restrictions = TextField(blank=True)
    multiple_run = CharField(max_length=20,
                             choices=yesno_options, default="No")

    def clone(self):
        new_class = Class()
        new_class.teacher = self.teacher
        new_class.minimum_enrollment = self.minimum_enrollment
        new_class.organization = self.organization
        new_class.type = self.type
        new_class.fee = self.fee
        new_class.other_teachers = self.other_teachers
        new_class.length_minutes = self.length_minutes
        new_class.history = self.history
        new_class.run_before = self.run_before
        new_class.space_needs = self.space_needs
        new_class.physical_restrictions = self.physical_restrictions
        new_class.multiple_run = self.multiple_run
        new_class.title = self.title
        new_class.description = self.description
        new_class.conference = Conference.objects.filter(
            status="upcoming").first()
        new_class.save()
        return new_class

    @property
    def get_space_needs(self):
        needs = ""
        for top, top_opts in space_options:
            for key, sub_level in top_opts:
                if key == self.space_needs:
                    needs = top + " - " + sub_level
        return needs

    @property
    def sched_payload(self):
        payload = {}
        details = {}
        details = {'type': self.type}
        if not self.fee == 0:
            details['fee'] = self.fee

        payload['details'] = details
        payload['title'] = self.event_ptr.title
        payload['description'] = self.event_ptr.description
        if not self.duration:
            self.duration = Duration(hours=1)
            self.save(update_fields=('duration',))
        payload['duration'] = self.duration.set_format("{1:0>2}:{2:0>2}")
        return payload

    @property
    def bio_payload(self):
        return [self.teacher]

    @property
    def calendar_type(self):
        return calendar_types[1]

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    @property
    def get_bid_fields(self):
        '''
        Returns fields, required_fields as tuple of lists
        '''
        return (['title',
                 'teacher',
                 'description',
                 'maximum_enrollment',
                 'type',
                 'fee',
                 'length_minutes',
                 'history',
                 'schedule_constraints',
                 'avoided_constraints',
                 'space_needs'],
                ['title',
                 'teacher',
                 'description',
                 'schedule_constraints'])

    @property
    def get_draft_fields(self):
        return (['title', 'teacher'])

    @property
    def schedule_ready(self):
        return self.accepted == 3

    @property
    def complete(self):
        return (self.title is not '' and
                self.teacher is not None and
                self.description is not '' and
                self.blurb is not ''
                )

    @property
    def bid_review_header(self):
        return (['Title',
                 'Teacher',
                 'Type',
                 'Last Update',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        return (self.title,
                self.teacher,
                self.type,
                self.updated_at.astimezone(pytz.timezone('America/New_York')),
                acceptance_states[self.accepted][1])

    def __str__(self):
        return self.title

    # tickets that apply to class are:
    #   - any ticket that applies to "most"
    #   - any ticket that applies to the conference
    #   - any ticket that links this event specifically
    # but for all tickets - iff the ticket is active
    #
    def get_tickets(self):
        from ticketing.models import TicketItem
        most_events = TicketItem.objects.filter(
            Q(bpt_event__include_most=True) |
            Q(bpt_event__include_conference=True)).filter(
                active=True,
                bpt_event__conference=self.conference)
        my_events = TicketItem.objects.filter(bpt_event__linked_events=self,
                                              active=True)
        tickets = list(chain(my_events, most_events))
        return tickets

    class Meta:
        verbose_name_plural = 'classes'
        app_label = "gbe"
