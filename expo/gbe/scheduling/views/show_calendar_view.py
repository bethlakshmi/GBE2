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
from gbe.scheduling.views.functions import show_general_status
from operator import itemgetter


class ShowCalendarView(View):
    template = 'gbe/scheduling/calendar.tmpl'
    calendar_type = None
    conference = None
    this_day = None
    grid_map = {
        5: 3,
        4: 3,
        3: 4,
        2: 6,
        1: 12,
    }

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
        if self.this_day:
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
        hour_block_size = {}
        for occurrence in occurrences:
            event = events.filter(pk=occurrence.eventitem.event.pk).first()
            hour = occurrence.start_time.strftime("%-I:00 %p")
            display_list += [{
                'start':  occurrence.start_time.strftime(TIME_FORMAT),
                'end': occurrence.end_time.strftime(TIME_FORMAT),
                'title': event.e_title,
                'location': occurrence.location,
                'hour': hour,
                'detail_link': reverse('detail_view',
                                       urlconf='scheduler.urls',
                                       args=[occurrence.eventitem.pk]),
            }]
            if hour in hour_block_size:
                hour_block_size[hour] += 1
            else:
                hour_block_size[hour] = 1
        return max(hour_block_size.values()), display_list

    def get(self, request, *args, **kwargs):
        context = self.process_inputs(request, args, kwargs)
        if not self.conference or not self.this_day or not self.calendar_type:
            return render(request, self.template, context)
        response = get_occurrences(
            labels=[self.calendar_type, self.conference.conference_slug],
            day=self.this_day.day)
        # temp hack, wait for update to master
        show_general_status(
            request, response, self.__class__.__name__)
        if len(response.occurrences) > 0:
            max_block_size, context[
                'occurrences'] = self.build_occurrence_display(
                response.occurrences)
            grid_size = 2
            if max_block_size < 6:
                grid_size = self.grid_map[max_block_size]
            context['grid_size'] = grid_size
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ShowCalendarView, self).dispatch(*args, **kwargs)
