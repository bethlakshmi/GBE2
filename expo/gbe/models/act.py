import pytz
from django.db.models import(
    CharField,
    ForeignKey,
    OneToOneField,
    TextField,
    URLField,
)
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ValidationError,
)
from gbe.models import (
    Biddable,
    Conference,
    Performer,
    TechInfo,
    visible_bid_query,
)
from gbetext import (
    acceptance_states,
    act_alerts,
    act_not_unique,
    video_options,
)
from scheduler.models import ActItem


class Act (Biddable, ActItem):
    '''
    A performance, either scheduled or proposed.
    Until approved, an Act is simply a proposal.
    '''
    performer = ForeignKey(Performer,
                           related_name='acts',
                           blank=True,
                           null=True)
    tech = OneToOneField(TechInfo, blank=True)
    video_link = URLField(blank=True)
    video_choice = CharField(max_length=2,
                             choices=video_options,
                             blank=True)
    shows_preferences = TextField(blank=True)
    other_performance = TextField(blank=True)
    why_you = TextField(blank=True)

    is_not_blank = ('len(%s) > 0', '%s cannot be blank')

    validation_list = [
        (('b_title', 'Title'), is_not_blank),
        (('b_description', 'Description'), is_not_blank),
    ]

    def clone(self):
        act = Act(
            performer=self.performer,
            tech=self.tech.clone(),
            video_link=self.video_link,
            video_choice=self.video_link,
            other_performance=self.other_performance,
            why_you=self.why_you,
            b_title=self.b_title,
            b_description=self.b_description,
            submitted=False,
            accepted=False,
            b_conference=Conference.objects.filter(
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
        return (self.performer.contact.display_name,
                self.contact_email,
                self.performer.contact.phone,
                self.accepted,
                self.b_title,
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
        show_name = ""
        for show in self.get_scheduled_shows():
            if len(show_name) > 0:
                show_name += ", %s" % str(show.eventitem)
            else:
                show_name = str(show.eventitem)

        return (self.performer.name,
                self.b_title,
                self.updated_at.astimezone(pytz.timezone('America/New_York')),
                acceptance_states[self.accepted][1],
                show_name)

    @property
    def complete(self):
        return (self.performer.complete and
                len(self.b_title) > 0 and
                len(self.b_description) > 0 and
                len(self.video_choice) > 0)

    def validate_unique(self, *args, **kwargs):
        # conference, title and performer contact should all be unique before
        # the act is saved.
        super(Act, self).validate_unique(*args, **kwargs)
        if Act.objects.filter(
                b_conference=self.b_conference,
                b_title=self.b_title,
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
             'b_title',
             'track_title',
             'track_artist',
             'track_duration',
             'act_duration',
             'video_link',
             'video_choice',
             'b_description',
             'why_you',
             'b_conference'],
            ['b_title', 'b_description', 'shows_preferences', 'performer', ],
        )

    @property
    def bid_draft_fields(self):
        return (['b_title', 'performer'])

    @property
    def sched_payload(self):
        return {'duration': self.tech.stage.act_duration,
                'title': self.b_title,
                'description': self.b_description,
                'details': {'type': 'act'}}

    @property
    def cast_shows(self):
        return (('No', 'No'), ('Yes', 'Yes'), ('Won', 'Yes - and Won!'))

    @property
    def bidder_is_active(self):
        return self.performer.contact.user_object.is_active

    def __str__(self):
        return "%s: %s" % (str(self.performer), self.b_title)

    class Meta:
        app_label = "gbe"
