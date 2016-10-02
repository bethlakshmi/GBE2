from django.conf import settings
from django.db.models import (
    BooleanField,
    CharField,
    DateField,
    FileField,
    ForeignKey,
    Model,
    OneToOneField,
    PositiveIntegerField,
    Q,
    SlugField,
    TextField,
    TimeField,
)

from gbetext import (
    conference_statuses,
)
from gbe_forms_text import *
from gbe.expomodelfields import DurationField


visible_bid_query = (Q(biddable_ptr__conference__status='upcoming') |
                     Q(biddable_ptr__conference__status='ongoing'))


class Conference(Model):
    conference_name = CharField(max_length=128)
    conference_slug = SlugField()
    status = CharField(choices=conference_statuses,
                       max_length=50,
                       default='upcoming')
    accepting_bids = BooleanField(default=False)

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


class ConferenceDay(Model):
    day = DateField(blank=True)
    conference = ForeignKey(Conference)

    def __unicode__(self):
        return self.day.strftime("%a, %b %d")

    class Meta:
        ordering = ['day']
        verbose_name = "Conference Day"
        verbose_name_plural = "Conference Days"
        app_label = "gbe"


class VolunteerWindow(Model):
    start = TimeField(blank=True)
    end = TimeField(blank=True)
    day = ForeignKey(ConferenceDay)

    def __unicode__(self):
        return "%s, %s to %s" % (str(self.day),
                                 self.start.strftime("%I:%M %p"),
                                 self.end.strftime("%I:%M %p"))

    class Meta:
        ordering = ['day', 'start']
        verbose_name = "Volunteer Window"
        verbose_name_plural = "Volunteer Windows"
        app_label = "gbe"
