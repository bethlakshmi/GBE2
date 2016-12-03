import os
import pytz 
from datetime import (
    datetime,
    timedelta
)
from expo.settings import (
    TIME_FORMAT,
)
from django.utils.formats import date_format
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
        return date_format(self.day, "DATE_FORMAT")

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
                                 date_format(self.start, "TIME_FORMAT"),
                                 date_format(self.end, "TIME_FORMAT"))

    def start_timestamp(self):
        return pytz.utc.localize(datetime.combine(self.day.day, self.start))

    def end_timestamp(self):
        return pytz.utc.localize(datetime.combine(self.day.day, self.end))

    def check_conflict(self, start, end):
        starttime = self.start_timestamp()
        endtime = self.end_timestamp()
        has_conflict = False

        if start == starttime:
            has_conflict = True
        elif (start > starttime and
              start < endtime):
            has_conflict = True
        elif (start < starttime and
              end > starttime):
            has_conflict = True
        return has_conflict

    class Meta:
        ordering = ['day', 'start']
        verbose_name = "Volunteer Window"
        verbose_name_plural = "Volunteer Windows"
        app_label = "gbe"
