import os
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
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
from datetime import datetime
from datetime import timedelta
from gbe.expomodelfields import DurationField
from django.core.urlresolvers import reverse
from scheduler.functions import (
    set_time_format,
    get_roles_from_scheduler
)
from model_utils.managers import InheritanceManager
from gbe.duration import Duration
import gbe
import pytz
from gbe.models import AvailableInterest


visible_bid_query = (Q(biddable_ptr__conference__status='upcoming') |
                     Q(biddable_ptr__conference__status='ongoing'))


class Conference(models.Model):
    conference_name = models.CharField(max_length=128)
    conference_slug = models.SlugField()
    status = models.CharField(choices=conference_statuses,
                              max_length=50,
                              default='upcoming')
    accepting_bids = models.BooleanField(default=False)

    def __unicode__(self):
        return self.conference_name

    @classmethod
    def current_conf(cls):
        return cls.objects.filter(status__in=('upcoming', 'ongoing')).first()

    @classmethod
    def by_slug(cls, slug):
        try:
            return cls.objects.get(conference_slug=slug)
        except cls.DoesNotExist:
            return cls.current_conf()

    @classmethod
    def all_slugs(cls):
        return cls.objects.order_by('-accepting_bids').values_list(
            'conference_slug', flat=True)

    def windows(self):
        return VolunteerWindow.objects.filter(day__conference=self)

    class Meta:
        verbose_name = "conference"
        verbose_name_plural = "conferences"
        app_label = "gbe"


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


###################
# Technical info #
###################

class AudioInfo(models.Model):
    '''
    Information about the audio required for a particular Act
    '''
    track_title = models.CharField(max_length=128, blank=True)
    track_artist = models.CharField(max_length=123, blank=True)
    track = models.FileField(upload_to='uploads/audio', blank=True)
    track_duration = DurationField(blank=True)
    need_mic = models.BooleanField(default=False, blank=True)
    own_mic = models.BooleanField(default=False, blank=True)
    notes = models.TextField(blank=True)
    confirm_no_music = models.BooleanField(default=False)

    @property
    def dump_data(self):
        return [self.track_title,
                self.track_artist,
                self.track,
                self.track_duration,
                self.need_mic,
                self.own_mic,
                self.notes,
                self.confirm_no_music
                ]

    def clone(self):
        ai = AudioInfo(track_title=self.track_title,
                       track_artist=self.track_artist,
                       track=self.track,
                       track_duration=self.track_duration,
                       need_mic=self.need_mic,
                       own_mic=self.own_mic,
                       notes=self.notes,
                       confirm_no_music=self.confirm_no_music)
        ai.save()
        return ai

    @property
    def is_complete(self):
        return bool(self.confirm_no_music or
                    (self.track_title and
                     self.track_artist and
                     self.track_duration
                     ))

    @property
    def incomplete_warnings(self):
        if self.is_complete:
            return {}
        else:
            return {'audio': audioinfo_incomplete_warning}

    def __unicode__(self):
        try:
            return "AudioInfo: " + self.techinfo.act.title
        except:
            return "AudioInfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'audio info'
        app_label = "gbe"


class LightingInfo (models.Model):
    '''
    Information about the basic (not related to cues) lighting
    needs of a particular Act
    '''
    notes = models.TextField(blank=True)
    costume = models.TextField(blank=True)
    specific_needs = models.TextField(blank=True)

    def clone(self):
        li = LightingInfo(notes=self.notes,
                          costume=self.costume)
        li.save()
        return li

    @property
    def dump_data(self):
        return [self.notes, self.costume]

    @property
    def is_complete(self):
        return True

    @property
    def incomplete_warnings(self):
        if self.is_complete:
            return {}
        else:
            return {"lighting": lightinginfo_incomplete_warning}

    def __unicode__(self):
        try:
            return "LightingInfo: " + self.techinfo.act.title
        except:
            return "LightingInfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'lighting info'
        app_label = "gbe"


class StageInfo(models.Model):
    '''
    Information about the stage requirements for a particular Act
    confirm field should be offered if the user tries to save with all
    values false and no notes
    '''
    act_duration = DurationField(blank=True)
    intro_text = models.TextField(blank=True)
    confirm = models.BooleanField(default=False)
    set_props = models.BooleanField(default=False)
    cue_props = models.BooleanField(default=False)
    clear_props = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def clone(self):
        si = StageInfo(act_duration=self.act_duration,
                       intro_text=self.intro_text,
                       confirm=self.confirm,
                       set_props=self.set_props,
                       cue_props=self.cue_props,
                       clear_props=self.clear_props,
                       notes=self.notes)
        si.save()
        return si

    @property
    def dump_data(self):
        return [self.act_duration,
                self.intro_text.encode('utf-8').strip(),
                self.confirm,
                self.set_props,
                self.cue_props,
                self.clear_props,
                self.notes.encode('utf-8').strip(),
                ]

    @property
    def is_complete(self):
        return bool(self.set_props or
                    self.clear_props or
                    self.cue_props or self.confirm)

    @property
    def incomplete_warnings(self):
        if self.is_complete:
            return {}
        else:
            return {'stage': stageinfo_incomplete_warning}

    def __unicode__(self):
        try:
            return "StageInfo: " + self.techinfo.act.title
        except:
            return "StageInfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'stage info'
        app_label = "gbe"


class TechInfo(models.Model):
    '''
    Gathers up technical info about an act in a show.
    BB - doing 2 additional cues for now for an easy add to existing DB
      2015  - may want to consider a many to many field for 1+ cues
    '''
    audio = models.OneToOneField(AudioInfo, blank=True)
    lighting = models.OneToOneField(LightingInfo, blank=True)
    stage = models.OneToOneField(StageInfo, blank=True)

    def clone(self):
        ti = TechInfo()
        ti.audio = self.audio.clone()
        ti.lighting = self.lighting.clone()
        ti.stage = self.stage.clone()
        ti.save()
        for ci in CueInfo.objects.filter(techinfo=self):
            ci.clone(self)
        return ti

    @property
    def is_complete(self):
        try:
            CueInfo.objects.get(techinfo=self, cue_sequence=0)
            cueinfopresent = True
        except CueInfo.DoesNotExist:
            cueinfopresent = False
        return bool(self.audio.is_complete and
                    self.lighting.is_complete and
                    self.stage.is_complete and
                    cueinfopresent)

    def get_incomplete_warnings(self):
        warnings = {}
        warnings.update(self.lighting.incomplete_warnings)
        warnings.update(self.audio.incomplete_warnings)
        warnings.update(self.stage.incomplete_warnings)
        return warnings

    def __unicode__(self):
        try:
            return "Techinfo: " + self.act.title
        except:
            return "Techinfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'tech info'
        app_label = "gbe"


class CueInfo(models.Model):
    '''
    Information about the lighting needs of a particular Act as they
    relate to one or more cues within the Act.  Each item is the change
    that occurs after a cue
    '''
    cue_sequence = models.PositiveIntegerField(default=0)
    cue_off_of = models.TextField()

    follow_spot = models.CharField(max_length=25,
                                   choices=follow_spot_options,
                                   default=follow_spot_options[0])

    center_spot = models.CharField(max_length=20,
                                   choices=offon_options, default="OFF")

    backlight = models.CharField(max_length=20,
                                 choices=offon_options, default="OFF")

    cyc_color = models.CharField(max_length=25,
                                 choices=cyc_color_options,
                                 default=cyc_color_options[0])

    wash = models.CharField(max_length=25,
                            choices=stage_lighting_options,
                            default=stage_lighting_options[0])
    sound_note = models.TextField(blank=True)
    techinfo = models.ForeignKey(TechInfo)

    def clone(self, techinfo):
        CueInfo(cue_sequence=self.cue_sequence,
                cue_off_of=self.cue_off_of,
                follow_spot=self.follow_spot,
                center_spot=self.center_spot,
                backlight=self.backlight,
                cyc_color=self.cyc_color,
                wash=self.wash,
                sound_note=self.sound_note,
                techinfo=techinfo).save()

    @property
    def is_complete(self):
        return bool(self.cue_off_of and self.cue_sequence and self.tech_info)

    def __unicode__(self):
        try:
            return "%s - cue %s" % (self.techinfo.act.title,
                                    str(self.cue_sequence))
        except:
            return "Cue: (deleted act) - %s" % str(self.cue_sequence)

    class Meta:
        verbose_name_plural = "cue info"
        app_label = "gbe"


#######
# Act #
#######


class Room(LocationItem):
    '''
    A room at the expo center
    '''
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    overbook_size = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        app_label = "gbe"


class ConferenceDay(models.Model):
    day = models.DateField(blank=True)
    conference = models.ForeignKey(Conference)

    def __unicode__(self):
        return self.day.strftime("%a, %b %d")

    class Meta:
        ordering = ['day']
        verbose_name = "Conference Day"
        verbose_name_plural = "Conference Days"
        app_label = "gbe"


class VolunteerWindow(models.Model):
    start = models.TimeField(blank=True)
    end = models.TimeField(blank=True)
    day = models.ForeignKey(ConferenceDay)

    def __unicode__(self):
        return "%s, %s to %s" % (str(self.day),
                                 self.start.strftime("%I:%M %p"),
                                 self.end.strftime("%I:%M %p"))

    class Meta:
        ordering = ['day', 'start']
        verbose_name = "Volunteer Window"
        verbose_name_plural = "Volunteer Windows"
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



class GenericEvent (Event):
    '''
    Any event except for a show or a class
    '''
    type = models.CharField(max_length=128,
                            choices=event_options,
                            blank=False,
                            default="Special")
    volunteer_type = models.ForeignKey(AvailableInterest,
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


class AdBid(Biddable):
    '''
    A bid for an ad. What sort of ad? Don't know yet. To do:
    use this
    '''
    company = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=128, choices=ad_type_options)

    def __unicode__(self):
        return self.company

    class Meta:
        app_label = "gbe"


class ArtBid(Biddable):
    '''
    Not used in 2015. Possibly in 2016
    '''
    bio = models.TextField(blank=True)
    works = models.TextField(blank=True)
    art1 = models.FileField(upload_to="uploads/images", blank=True)
    art2 = models.FileField(upload_to="uploads/images", blank=True)
    art3 = models.FileField(upload_to="uploads/images", blank=True)

    def __unicode__(self):
        return self.bidder.display_name

    class Meta:
        app_label = "gbe"


class ClassProposal(models.Model):
    '''
    A proposal for a class that someone else ought to teach.
    This is NOT a class bid, this is just a request that someone
    implement this idea.
    '''
    title = models.CharField(max_length=128)
    name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(blank=True)
    proposal = models.TextField()
    type = models.CharField(max_length=20,
                            choices=class_proposal_choices,
                            default='Class')
    display = models.BooleanField(default=False)
    conference = models.ForeignKey(
        Conference,
        default=lambda: Conference.objects.filter(status="upcoming").first())

    def __unicode__(self):
        return self.title

    @property
    def bid_review_header(self):
        return (['Title',
                 'Proposal',
                 'Type',
                 'Submitter',
                 'Published',
                 'Action'])

    @property
    def bid_review_summary(self):
        if self.display:
            published = "Yes"
        else:
            published = ""
        return (self.title, self.proposal, self.type, self.name, published)

    @property
    def presenter_bid_header(self):
        return (['Title', 'Proposal'])

    @property
    def presenter_bid_info(self):
        return (self.title, self.proposal, self.type)

    class Meta:
        app_label = "gbe"
