import os
from expo.settings import (
    DATETIME_FORMAT,
    TIME_FORMAT,
)
from django.utils.formats import date_format
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.core.exceptions import (
    ValidationError,
    NON_FIELD_ERRORS,
)
from itertools import chain
from scheduler.models import (
    Schedulable,
    EventItem,
    LocationItem,
    WorkerItem,
    ActItem,
    ResourceAllocation
)
from gbetext import *
from gbe_forms_text import *
from gbe.expomodelfields import DurationField
from scheduler.functions import (
    get_roles_from_scheduler
)
from model_utils.managers import InheritanceManager
from gbe.duration import Duration
import gbe
import pytz
from gbe.models import (
    Conference,
    Performer,
    Persona,
    Profile,
    Room,
    TechInfo,
    VolunteerWindow,
)
from gbe.ticketing_idd_interface import get_tickets


visible_bid_query = (Q(biddable_ptr__conference__status='upcoming') |
                     Q(biddable_ptr__conference__status='ongoing'))


class Biddable(models.Model):
    '''
    Abstract base class for items which can be Bid
    Essentially, specifies that we want something with a title
    '''
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    submitted = models.BooleanField(default=False)
    accepted = models.IntegerField(choices=acceptance_states,
                                   default=0,
                                   blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    conference = models.ForeignKey(
        Conference,
        default=lambda: Conference.objects.filter(status="upcoming").first())

    class Meta:
        verbose_name = "biddable item"
        verbose_name_plural = "biddable items"
        app_label = "gbe"

    def __unicode__(self):
        return self.title

    def typeof(self):
        return self.__class__

    @property
    def ready_for_review(self):
        return (self.submitted and
                self.accepted == 0)

    @property
    def is_current(self):
        return self.conference.status in ("upcoming", "current")



#######
# Act #
#######
class Act (Biddable, ActItem):
    '''
    A performance, either scheduled or proposed.
    Until approved, an Act is simply a proposal.
    '''
    performer = models.ForeignKey(Performer,
                                  related_name='acts',
                                  blank=True,
                                  null=True)
    tech = models.OneToOneField(TechInfo, blank=True)
    video_link = models.URLField(blank=True)
    video_choice = models.CharField(max_length=2,
                                    choices=video_options,
                                    blank=True)
    shows_preferences = models.TextField(blank=True)
    other_performance = models.TextField(blank=True)
    why_you = models.TextField(blank=True)

    is_not_blank = ('len(%s) > 0', '%s cannot be blank')

    validation_list = [
        (('title', 'Title'), is_not_blank),
        (('description', 'Description'), is_not_blank),
    ]

    def clone(self):
        act = Act(
            performer=self.performer,
            tech=self.tech.clone(),
            video_link=self.video_link,
            video_choice=self.video_link,
            other_performance=self.other_performance,
            why_you=self.why_you,
            title=self.title,
            description=self.description,
            submitted=False,
            accepted=False,
            conference=Conference.objects.filter(
                status="upcoming").first()
        )
        act.save()
        return act

    def get_performer_profiles(self):
        '''
        Gets all of the performers involved in the act.
        '''
        return self.performer.get_profiles()

    def typeof(self):
        return self.__class__

    @property
    def audio(self):
        if self.tech and self.tech.audio:
            return self.tech.audio
        return None

    @property
    def contact_info(self):
        return (self.title,
                self.contact_email,
                self.accepted,
                self.performer.contact.phone,
                self.performer.contact.display_name,
                )

    @property
    def contact_email(self):
        return self.performer.contact_email

    @property
    def contact_phone(self):
        return self.performer.contact_phone

    @property
    def bio(self):
        return self.performer

    @property
    def schedule_ready(self):
        return self.accepted == 3

    @property
    def schedule_headers(self):
        # This list can change
        return ['Performer',
                'Act Title',
                'Photo Link',
                'Video Link',
                'Bio Link',
                'Order']

    @property
    def visible(self, current=True):
        return self.accepted == 3

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    @property
    def bid_review_header(self):
        return (['Performer',
                 'Act Title',
                 'Last Update',
                 'State',
                 'Show',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        try:
            casting = ResourceAllocation.objects.filter(
                resource__actresource___item=self.resourceitem_id)[0]
            show_name = casting.event
        except:
            show_name = ''

        return (self.performer.name,
                self.title,
                self.updated_at.astimezone(pytz.timezone('America/New_York')),
                acceptance_states[self.accepted][1],
                show_name)

    @property
    def complete(self):
        return (self.performer.complete and
                len(self.title) > 0 and
                len(self.description) > 0 and
                len(self.intro_text) > 0 and
                len(self.video_choice) > 0)

    def validate_unique(self, *args, **kwargs):
        # conference, title and performer contact should all be unique before
        # the act is saved.
        super(Act, self).validate_unique(*args, **kwargs)
        if Act.objects.filter(
                conference=self.conference,
                title=self.title,
                performer__contact=self.performer.contact
        ).exclude(pk=self.pk).exists():
            raise ValidationError({
                NON_FIELD_ERRORS: [act_not_unique, ]
            })

    @property
    def alerts(self):
        '''
        Return a list of alerts pertaining to this object
        '''
        this_act_alerts = []
        if self.complete:
            if self.submitted:
                this_act_alerts.append(
                    act_alerts['act_complete_submitted'] % self.id)
            else:
                this_act_alerts.append(
                    act_alerts['act_complete_not_submitted'] % self.id)
        else:
            if self.submitted:
                this_act_alerts.append(
                    act_alerts['act_incomplete_submitted'] % self.id)
            else:
                this_act_alerts.append(
                    act_alerts['act_incomplete_not_submitted'] % self.id)
        return this_act_alerts

    @property
    def bid_fields(self):
        return (
            ['performer',
             'shows_preferences',
             'other_performance',
             'title',
             'track_title',
             'track_artist',
             'track_duration',
             'act_duration',
             'video_link',
             'video_choice',
             'description',
             'why_you'],
            ['title', 'description', 'shows_preferences', 'performer', ],
        )

    @property
    def bid_draft_fields(self):
        return (['title', 'performer'])

    @property
    def sched_payload(self):
        return {'duration': self.tech.stage.act_duration,
                'title': self.title,
                'description': self.description,
                'details': {'type': 'act'}}

    @property
    def cast_shows(self):
        return (('No', 'No'), ('Yes', 'Yes'), ('Won', 'Yes - and Won!'))

    def __str__(self):
        return "%s: %s" % (str(self.performer), self.title)

    class Meta:
        app_label = "gbe"


class Event(EventItem):
    '''
    Event is the base class for any scheduled happening at the expo.
    Events fall broadly into "shows" and "classes". Classes break down
    further into master classes, panels, workshops, etc. Shows are not
    biddable (though the Acts comprising them are) , but classes arise
    from participant bids.
    '''
    objects = InheritanceManager()
    title = models.CharField(max_length=128)
    description = models.TextField()            # public-facing description
    blurb = models.TextField(blank=True)        # short description
    duration = DurationField()
    notes = models.TextField(blank=True)  # internal notes about this event
    event_id = models.AutoField(primary_key=True)
    conference = models.ForeignKey(
        Conference,
        default=lambda: Conference.objects.filter(status="upcoming").first())
    default_location = models.ForeignKey(
        Room,
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


class Show (Event):
    '''
    A Show is an Event consisting of a sequence of Acts.
    Future to do: remove acts as field of this class, do acceptance
    and scheduling through scheduler  (post 2015)
    '''
    acts = models.ManyToManyField(Act, related_name="appearing_in", blank=True)
    cue_sheet = models.CharField(max_length=128,
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
        return get_tickets(self, most=True)

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


class Class(Biddable, Event):
    '''
    A Class is an Event where one or a few people
    teach/instruct/guide/mediate and a number of participants
    spectate/participate.
    '''
    teacher = models.ForeignKey(Persona,
                                related_name='is_teaching')
    # registration = models.ManyToManyField(Profile,
    #                                      related_name='classes',
    #                                      blank=True)
    minimum_enrollment = models.IntegerField(blank=True, default=1)
    maximum_enrollment = models.IntegerField(blank=True, default=20, null=True)
    organization = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=128,
                            choices=class_options,
                            blank=True,
                            default="Lecture")
    fee = models.IntegerField(blank=True, default=0, null=True)
    other_teachers = models.CharField(max_length=128, blank=True)
    length_minutes = models.IntegerField(choices=class_length_options,
                                         default=60, blank=True)
    history = models.TextField(blank=True)
    run_before = models.TextField(blank=True)
    schedule_constraints = models.TextField(blank=True)
    avoided_constraints = models.TextField(blank=True)
    space_needs = models.CharField(max_length=128,
                                   choices=space_options,
                                   blank=True,
                                   default='Please Choose an Option')
    physical_restrictions = models.TextField(blank=True)
    multiple_run = models.CharField(max_length=20,
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
        return get_tickets(self, most=True, conference=True)

    class Meta:
        verbose_name_plural = 'classes'
        app_label = "gbe"


class Volunteer(Biddable):
    '''
    Represents a conference attendee's participation as a volunteer.
    '''
    profile = models.ForeignKey(Profile, related_name="volunteering")
    number_shifts = models.IntegerField(choices=volunteer_shift_options,
                                        default=1)
    availability = models.TextField(blank=True)
    unavailability = models.TextField(blank=True)
    opt_outs = models.TextField(blank=True)
    pre_event = models.BooleanField(choices=boolean_options, default=False)
    background = models.TextField(blank=True)
    available_windows = models.ManyToManyField(
        VolunteerWindow,
        related_name="availablewindow_set",
        blank=True)
    unavailable_windows = models.ManyToManyField(
        VolunteerWindow,
        related_name="unavailablewindow_set",
        blank=True)

    def __unicode__(self):
        return self.profile.display_name

    @property
    def interest_list(self):
        return [
            interest.interest.interest
            for interest in self.volunteerinterest_set.filter(rank__gt=3)]

    @property
    def bid_review_header(self):
        return (['Name',
                 'Email',
                 'Hotel',
                 '# of Hours',
                 'Scheduling Info',
                 'Interests',
                 'Pre-event',
                 'Background',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        interest_string = ''
        for interest in self.interest_list:
            interest_string += interest + ', \n'
        availability_string = ''
        unavailability_string = ''
        for window in self.available_windows.all():
            availability_string += unicode(window) + ', \n'
        for window in self.unavailable_windows.all():
            unavailability_string += unicode(window) + ', \n'

        commitments = ''

        for event in self.profile.get_schedule(self.conference):
            start_time = date_format(event.start_time, "DATETIME_FORMAT")
            end_time = date_format(event.end_time, "TIME_FORMAT")

            commitment_string = "%s - %s to %s, \n " % (
                str(event),
                start_time,
                end_time)
            commitments += commitment_string
        format_string = "Availability: %s\n Conflicts: %s\n Commitments: %s"
        scheduling = format_string % (availability_string,
                                      unavailability_string,
                                      commitments)
        return (self.profile.display_name,
                self.profile.user_object.email,
                self.profile.preferences.in_hotel,
                self.number_shifts,
                scheduling,
                interest_string,
                self.pre_event,
                self.background,
                acceptance_states[self.accepted][1])

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    def check_available(self, start, end):
        available = "Not Available"
        for window in self.available_windows.all():
            starttime = window.start_timestamp()
            endtime = window.end_timestamp()
            if start == starttime:
                available = "Available"
            elif (start > starttime and
                  start < endtime):
                available = "Available"
            elif (start < starttime and
                  end > starttime):
                available = "Available"
        return available

    class Meta:
        app_label = "gbe"


class Vendor(Biddable):
    '''
    A request for space in the Expo marketplace.
    Note that company name is stored in the title field inherited
    from Biddable, and description is also inherited
    '''
    profile = models.ForeignKey(Profile)
    website = models.URLField(blank=True)
    physical_address = models.TextField()  # require physical address
    publish_physical_address = models.BooleanField(default=False)
    logo = models.FileField(upload_to="uploads/images", blank=True)
    want_help = models.BooleanField(choices=boolean_options,
                                    blank=True,
                                    default=False)
    help_description = models.TextField(blank=True)
    help_times = models.TextField(blank=True)

    def __unicode__(self):
        return self.title  # "title" here is company name

    def clone(self):
        vendor = Vendor(profile=self.profile,
                        website=self.website,
                        physical_address=self.physical_address,
                        publish_physical_address=self.publish_physical_address,
                        logo=self.logo,
                        want_help=self.want_help,
                        help_description=self.help_description,
                        help_times=self.help_times,
                        title=self.title,
                        description=self.description,
                        conference=Conference.objects.filter(
                            status="upcoming").first())

        vendor.save()
        return vendor

    @property
    def bid_review_header(self):
        return (['Bidder',
                 'Business Name',
                 'Website',
                 'Last Update',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        return (self.profile.display_name, self.title, self.website,
                self.updated_at.astimezone(pytz.timezone('America/New_York')),
                acceptance_states[self.accepted][1])

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    class Meta:
        app_label = "gbe"


class Costume(Biddable):
    '''
    An offer to display a costume at the Expo's costume display
      - profile is required, persona is optional
      - debut date is a text string to allow vague descriptions
      - act_title is optional, and therefore does not fit the rules of
        Biddable's title
    '''
    profile = models.ForeignKey(Profile, related_name="costumes")
    performer = models.ForeignKey(Persona, blank=True, null=True)
    creator = models.CharField(max_length=128)
    act_title = models.CharField(max_length=128, blank=True, null=True)
    debut_date = models.CharField(max_length=128, blank=True, null=True)
    active_use = models.BooleanField(choices=boolean_options, default=True)
    pieces = models.PositiveIntegerField(blank=True,
                                         null=True,
                                         validators=[MinValueValidator(1),
                                                     MaxValueValidator(20)])
    pasties = models.BooleanField(choices=boolean_options, default=False)
    dress_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)])
    more_info = models.TextField(blank=True)
    picture = models.FileField(upload_to="uploads/images", blank=True)

    @property
    def bid_fields(self):
        return (
            ['title',
             'performer',
             'creator',
             'act_title',
             'debut_date',
             'active_use',
             'pieces',
             'description',
             'pasties',
             'dress_size',
             'more_info',
             'picture'],
            ['title',
             'creator',
             'active_use',
             'pieces',
             'description',
             'pasties',
             'dress_size',
             'picture']
        )

    @property
    def bid_draft_fields(self):
        return (['title'])

    @property
    def bid_review_header(self):
        return (['Performer (Creator)',
                 'Title',
                 'Act',
                 'Last Update',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        name = ""
        if self.performer:
            name += self.performer.name + " "

        name += "(" + self.creator + ")"
        return (name,
                self.title,
                self.act_title,
                self.updated_at.astimezone(pytz.timezone('America/New_York')),
                acceptance_states[self.accepted][1])

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    class Meta:
        app_label = "gbe"
