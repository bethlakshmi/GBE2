from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import Http404
from django.core.urlresolvers import reverse
from gbetext import calendar_type as calendar_type_options
from django.utils.formats import date_format
from expo.settings import (
    TIME_FORMAT,
    URL_DATE,
)
from datetime import (
    datetime,
    timedelta,
)
from gbe.models import (
    ConferenceDay,
    Event,
)
from gbe.functions import (
    get_current_conference,
    get_conference_days,
    get_conference_by_slug,
    conference_slugs,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status


class ManageEventsView(View):
    template = 'gbe/scheduling/manage_event.tmpl'
    calendar_type = None
    conference = None
    this_day = None

    def process_inputs(self, request, args, kwargs):
        context = {}
        self.calendar_type = None
        self.conference = None
        self.this_day = None

        if "conference_slug" in kwargs:
            self.conference = get_conference_by_slug(
                kwargs['conference_slug'])
        else:
            self.conference = get_current_conference()

        if "calendar_type" in self.request.GET:
            self.calendar_type = self.request.GET.get('calendar_type', None)

        if "day" in self.request.GET:
            self.this_day = get_object_or_404(
                ConferenceDay,
                day=datetime.strptime(self.request.GET.get('day', None),
                                      URL_DATE))
            self.conference = self.this_day.conference
        else:
            self.this_day = get_conference_days(
                self.conference,
                open_to_public=True).order_by("day").first()

        context = {
            'calendar_type': self.calendar_type,
            'conference': self.conference,
            'conference_slugs': conference_slugs(),
            'this_day': self.this_day,
            'all_days': get_conference_days(self.conference),
            'calendar_type_options': calendar_type_options,
        }

        return context

    def get(self, request, *args, **kwargs):
        context = self.process_inputs(request, args, kwargs)
        search_labels = [self.conference.conference_slug, ]
        if self.calendar_type:
            search_labels += [self.calendar_type]
        response = get_occurrences(
            labels=search_labels,
            day=self.this_day.day)
        show_general_status(
            request, response, self.__class__.__name__)

        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ManageEventsView, self).dispatch(*args, **kwargs)
