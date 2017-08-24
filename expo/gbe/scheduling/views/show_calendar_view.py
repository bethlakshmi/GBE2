from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
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
from expo.settings import URL_DATE
from datetime import (
    datetime,
    timedelta,
)
from gbe.models import ConferenceDay
from gbe.functions import (
    get_current_conference,
    get_conference_days,
    get_conference_by_slug,
    conference_slugs,
)

class ShowCalendarView(View):
    template = 'gbe/scheduling/calendar.tmpl'
    @property

    def groundwork(self, request, args, kwargs):
        pass

    def process_inputs(self, request, args, kwargs):
        context = {}
        calendar_type = None
        conference = None
        this_day = None

        if "calendar_type" in kwargs:
            calendar_type = kwargs['calendar_type']
            if calendar_type not in calendar_type_options.values():
                raise Http404
        else:
            raise Http404

        if "day" in self.request.GET:
            this_day = get_object_or_404(
                ConferenceDay,
                day=datetime.strptime(self.request.GET.get('day', None), URL_DATE))
            conference = this_day.conference

        if not conference and "conference" in self.request.GET:
            conference = get_conference_by_slug(
                self.request.GET.get('conference', None))
        elif not conference:
            conference = get_current_conference()

        if not this_day:
            this_day = get_conference_days(conference).order_by("day").first()

        context = {
            'calendar_type': calendar_type,
            'conference': conference,
            'conference_slugs': conference_slugs(),
            'this_day': this_day,
        }

        if this_day:
            if ConferenceDay.objects.filter(
                    day=this_day.day+timedelta(days=1)).exists():
                context['next_date'] = (this_day.day+timedelta(days=1)
                                        ).strftime(URL_DATE)
            if ConferenceDay.objects.filter(
                    day=this_day.day-timedelta(days=1)).exists():
                context['prev_date'] = (this_day.day-timedelta(days=1)
                                        ).strftime(URL_DATE)

        return context

    def get(self, request, *args, **kwargs):
        context = self.process_inputs(request, args, kwargs)
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ShowCalendarView, self).dispatch(*args, **kwargs)
