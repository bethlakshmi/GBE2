from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import Http404
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
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
from gbe.scheduling.forms import SelectEventForm
from expo.settings import (
    DATE_FORMAT,
    DATETIME_FORMAT,
)
from datetime import datetime
from gbetext import calendar_type as calendar_type_options


class ManageEventsView(View):
    template = 'gbe/scheduling/manage_event.tmpl'
    calendar_type = None
    conference = None
    this_day = None

    def setup(self, request, args, kwargs):
        context = {}
        self.calendar_type = None
        self.conference = None
        self.this_day = None

        if "conference_slug" in kwargs:
            self.conference = get_conference_by_slug(
                kwargs['conference_slug'])
        else:
            self.conference = get_current_conference()

        self.day_list = []
        for day in self.conference.conferenceday_set.all():
            self.day_list += [(day.pk, day.day.strftime(DATE_FORMAT))]

        context = {
            'conference': self.conference,
            'conference_slugs': conference_slugs(),
        }

        return context

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.setup(request, args, kwargs)
        select_form = SelectEventForm(prefix="event-select")
        select_form.fields['day'].choices = self.day_list
        context['selection_form'] = select_form

        return render(request, self.template, context)

    def build_occurrence_display(self, occurrences):
        display_list = []
        events = Event.objects.filter(
            e_conference=self.conference).select_subclasses()
        for occurrence in occurrences:
            event = events.filter(pk=occurrence.eventitem.event.pk).first()
            display_list += [{
                'start':  occurrence.start_time.strftime(DATETIME_FORMAT),
                'title': event.e_title,
                'location': occurrence.location,
                'duration': event.duration.hours() + float(
                    event.duration.minutes())/60,
                'type': event.event_type,
                'current_volunteer': occurrence.volunteer_count,
                'max_volunteer': occurrence.max_volunteer,
                'detail_link': reverse('detail_view',
                                       urlconf='scheduler.urls',
                                       args=[event.eventitem_id]),
                'create_link': reverse('create_event_schedule',
                                       urlconf='gbe.scheduling.urls',
                                       args=[event.__class__.__name__,
                                             event.eventitem_id]),
                'edit_link': reverse('edit_event_schedule',
                                        urlconf='gbe.scheduling.urls',
                                        args=[event.__class__.__name__,
                                              event.eventitem_id,
                                              occurrence.id]),
                'delete_link': reverse('delete_schedule',
                                          urlconf='scheduler.urls',
                                          args=[occurrence.pk]),

            }]
        return display_list

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.setup(request, args, kwargs)
        select_form = SelectEventForm(request.POST,
                                      prefix="event-select")
        select_form.fields['day'].choices = self.day_list
        context['selection_form'] = select_form
        if not select_form.is_valid():
            return render(request, self.template, context)
        occurrences = []
        if len(select_form.cleaned_data['day']) > 0:
            for day_id in select_form.cleaned_data['day']:
                day = ConferenceDay.objects.get(pk=day_id)
                if len(select_form.cleaned_data['calendar_type']) > 0:
                    for cal_type in select_form.cleaned_data['calendar_type']:
                        response = get_occurrences(
                            labels=[
                                self.conference.conference_slug,
                                calendar_type_options[int(cal_type)]],
                            day=day.day)
                        occurrences += response.occurrences
                else:
                    response = get_occurrences(labels=[
                        self.conference.conference_slug, ],
                        day=day.day)
                    occurrences += response.occurrences
        else:
            if len(select_form.cleaned_data['calendar_type']) > 0:
                for cal_type in select_form.cleaned_data['calendar_type']:
                    response = get_occurrences(
                        labels=[
                            self.conference.conference_slug,
                            calendar_type_options[int(cal_type)]])
                    occurrences += response.occurrences

            else:
                response = get_occurrences(labels=[
                    self.conference.conference_slug, ])
                occurrences += response.occurrences
        context['occurrences'] = self.build_occurrence_display(occurrences)
        return render(request, self.template, context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageEventsView, self).dispatch(*args, **kwargs)
