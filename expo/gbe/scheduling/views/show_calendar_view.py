from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
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
from gbe.scheduling.views.functions import show_scheduling_occurrence_status

class ShowCalendarView(View):
    template = 'gbe/scheduling/calendar.tmpl'
    calendar_type = None
    conference = None
    this_day = None

    def groundwork(self, request, args, kwargs):
        pass

    def process_inputs(self, request, args, kwargs):
        context = {}
        self.calendar_type = None
        self.conference = None
        self.this_day = None

        if "calendar_type" in kwargs:
            self.calendar_type = kwargs['calendar_type']
            if self.calendar_type not in calendar_type_options.values():
                raise Http404
        else:
            raise Http404

        if "day" in self.request.GET:
            self.this_day = get_object_or_404(
                ConferenceDay,
                day=datetime.strptime(self.request.GET.get('day', None),
                                      URL_DATE))
            self.conference = self.this_day.conference

        if not self.conference and "conference" in self.request.GET:
            self.conference = get_conference_by_slug(
                self.request.GET.get('conference', None))
        elif not self.conference:
            self.conference = get_current_conference()

        if not self.this_day:
            self.this_day = get_conference_days(
                self.conference).order_by("day").first()

        context = {
            'calendar_type': self.calendar_type,
            'conference': self.conference,
            'conference_slugs': conference_slugs(),
            'this_day': self.this_day,
        }

        if ConferenceDay.objects.filter(
                day=self.this_day.day+timedelta(days=1)).exists():
            context['next_date'] = (self.this_day.day+timedelta(days=1)
                                    ).strftime(URL_DATE)
        if ConferenceDay.objects.filter(
                day=self.this_day.day-timedelta(days=1)).exists():
            context['prev_date'] = (self.this_day.day-timedelta(days=1)
                                    ).strftime(URL_DATE)

        return context

    def build_occurrence_display(self, occurrences):
        display_list = []
        events = Event.objects.filter(e_conference=self.conference)
        for occurrence in occurrences:
            event = events.filter(pk=occurrence.eventitem.event.pk).first()
            display_list += [{
                'start':  occurrence.start_time.strftime(TIME_FORMAT),
                'end': occurrence.end_time.strftime(TIME_FORMAT),
                'title': event.e_title,
                'location': occurrence.location,
                'hour': occurrence.start_time.hour
            }]
        return display_list

    def get(self, request, *args, **kwargs):
        context = self.process_inputs(request, args, kwargs)
        response = get_occurrences(
            labels=[self.calendar_type, self.conference.conference_slug],
            day=self.this_day.day)
        # temp hack, wait for update to master
        response.occurrence = None
        show_scheduling_occurrence_status(request, response, self.__class__.__name__)
        if len(response.occurrences) > 0:
            context['occurrences'] = self.build_occurrence_display(response.occurrences)
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ShowCalendarView, self).dispatch(*args, **kwargs)
