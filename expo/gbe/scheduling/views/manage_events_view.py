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
    AvailableInterest,
    ConferenceDay,
    Event,
    GenericEvent,
)
from gbe.functions import (
    get_current_conference,
    get_conference_days,
    get_conference_by_slug,
    conference_list,
    validate_perms,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.scheduling.forms import (
    HiddenSelectEventForm,
    SelectEventForm,
)
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
        validate_perms(request, ('Scheduling Mavens',))
        context = {}
        self.calendar_type = None
        self.conference = None
        conference_set = conference_list().order_by('-conference_slug')
        self.this_day = None

        if "conference_slug" in kwargs:
            self.conference = get_conference_by_slug(
                kwargs['conference_slug'])
        else:
            self.conference = get_current_conference()

        day_list = []
        for day in self.conference.conferenceday_set.all():
            day_list += [(day.pk, day.day.strftime(DATE_FORMAT))]
        
        select_form = SelectEventForm(request.GET,
                                      prefix=self.conference.conference_slug)
        select_form.fields['day'].choices = day_list
        context = {
            'conference': self.conference,
            'conference_slugs': [
                conf.conference_slug for conf in conference_set],
            'selection_form': select_form,
            'other_forms': [],
        }
        if 'new' in request.GET.keys():
            context['success_occurrence'] = int(request.GET['new'])
        for conf in conference_set:
            if self.conference != conf:
                hidden_form = HiddenSelectEventForm(
                    request.GET,
                    prefix=conf.conference_slug)
                conf_day_list = []
                for day in conf.conferenceday_set.all():
                    conf_day_list += [(day.pk, day.day.strftime(DATE_FORMAT))]
                hidden_form.fields['day'].choices = conf_day_list
                context['other_forms'] += [hidden_form]
        return context

    def build_occurrence_display(self, occurrences):
        display_list = []
        events = Event.objects.filter(e_conference=self.conference)
        for occurrence in occurrences:
            display_item = {
                'id': occurrence.id,
                'sort_start': occurrence.start_time,
                'start':  occurrence.start_time.strftime(DATETIME_FORMAT),
                'title': occurrence.eventitem.event.e_title,
                'location': occurrence.location,
                'duration': occurrence.eventitem.event.duration.hours(
                    ) + float(
                    occurrence.eventitem.event.duration.minutes())/60,
                'type': events.filter(
                    eventitem_id=occurrence.eventitem.eventitem_id
                    ).get_subclass().event_type,
                'current_volunteer': occurrence.volunteer_count,
                'max_volunteer': occurrence.max_volunteer,
                'detail_link': reverse(
                    'detail_view',
                    urlconf='scheduler.urls',
                    args=[occurrence.eventitem.event.eventitem_id]),
                'delete_link': reverse('delete_schedule',
                                       urlconf='scheduler.urls',
                                       args=[occurrence.id])}
            if self.conference.status != "completed":
                display_item['create_link'] = reverse(
                    'create_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=[occurrence.eventitem.event.__class__.__name__,
                          occurrence.eventitem.event.eventitem_id])
                display_item['edit_link'] = reverse(
                    'edit_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=[occurrence.eventitem.event.__class__.__name__,
                          occurrence.eventitem.event.eventitem_id,
                          occurrence.id])
            display_list += [display_item]

        display_list.sort(key=lambda k: k['sort_start'])
        return display_list

    def get_filtered_occurences(self, request, select_form):
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
        elif len(select_form.cleaned_data['calendar_type']) > 0:
            for cal_type in select_form.cleaned_data['calendar_type']:
                response = get_occurrences(
                    labels=[
                        self.conference.conference_slug,
                        calendar_type_options[int(cal_type)]])
                occurrences += response.occurrences
        else:
            response = get_occurrences(
                labels=[
                    self.conference.conference_slug,])
            occurrences += response.occurrences
        if len(select_form.cleaned_data['volunteer_type']) > 0:
            volunteer_event_ids = GenericEvent.objects.filter(
                e_conference=self.conference,
                volunteer_type__in=select_form.cleaned_data['volunteer_type']
                ).values_list('eventitem_id', flat=True)
            occurrences = [
                occurrence for occurrence in occurrences
                if occurrence.eventitem.eventitem_id in volunteer_event_ids]
        return self.build_occurrence_display(occurrences)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.setup(request, args, kwargs)

        if context['selection_form'].is_valid() and (
                len(context['selection_form'].cleaned_data['day']) > 0 or len(
                    context['selection_form'].cleaned_data[
                        'calendar_type'])) > 0 or (
                'volunteer_type' in context['selection_form'].cleaned_data and len(
                    context['selection_form'].cleaned_data['volunteer_type']) > 0):
            context['occurrences'] = self.get_filtered_occurences(
                request,
                context['selection_form'])
        return render(request, self.template, context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageEventsView, self).dispatch(*args, **kwargs)
