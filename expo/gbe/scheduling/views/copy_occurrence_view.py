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
from gbe.scheduling.forms import (
    CopyEventForm,
    CopyEventPickDayForm,
    CopyEventPickModeForm,
)
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    get_occurrences,
)
from gbe.scheduling.views.functions import (
    show_general_status,
    show_scheduling_occurrence_status,
)
from gbe.models import (
    Conference,
    ConferenceDay,
    Event,
)
from gbe.functions import validate_perms
from gbe.duration import Duration
from gbe.views.class_display_functions import get_scheduling_info
from datetime import timedelta


class CopyOccurrenceView(View):
    template = 'gbe/scheduling/copy_wizard.tmpl'
    permissions = ('Scheduling Mavens',)
    copy_date_format = "%a, %b %-d, %Y %-I:%M %p"
    occurrence = None
    children = []
    future_days = None

    def groundwork(self, request, args, kwargs):
        self.occurrence_id = int(kwargs['occurrence_id'])
        self.profile = validate_perms(request, self.permissions)
        response = get_occurrence(self.occurrence_id)
        show_general_status(request, response, self.__class__.__name__)
        if not response.occurrence:
            raise Http404
        self.occurrence = response.occurrence
        response = get_occurrences(parent_event_id=self.occurrence_id)
        self.children = response.occurrences
        show_general_status(request, response, self.__class__.__name__)

    def make_context(self, request):
        context = {
            'first_title': "Copying - %s: %s" % (
                self.occurrence.eventitem.event.e_title,
                self.occurrence.starttime.strftime(self.copy_date_format))}
        if self.children and len(self.children) > 0:
            context['copy_mode'] = CopyEventPickModeForm(
                event_type=self.occurrence.as_subtype.event_type)

        else:
            context['pick_day'] = CopyEventPickDayForm()
            context['pick_day'].fields['copy_to_day'].empty_label = None
            context['pick_day'].fields['copy_to_day'].required = True
        return render(
            request,
            self.template,
            context)

    def build_mode_form(self, request):
        context = {
            'first_title': "Copying - %s: %s" % (
                self.occurrence.eventitem.event.e_title,
                self.occurrence.starttime.strftime(self.copy_date_format))}
        if self.children and len(self.children) > 0:
            context['copy_mode'] = CopyEventPickModeForm(
                request.POST,
                event_type=self.occurrence.as_subtype.event_type)
        else:
            context['pick_day'] = CopyEventPickDayForm(request.POST)
            context['pick_day'].fields['copy_to_day'].empty_label = None
            context['pick_day'].fields['copy_to_day'].required = True
        return context

    def validate_and_proceed(self, request, context):
        make_copy = False
        if 'copy_mode' in context.keys() and context['copy_mode'].is_valid():
            if context['copy_mode'].cleaned_data[
                    'copy_mode'] == "copy_children_only":
                response = get_occurrence(
                    context['copy_mode'].cleaned_data['target_event'])
                context['second_title'] = "Destination is %s: %s" % (
                    response.occurrence.eventitem.event.e_conference.conference_slug,
                    response.occurrence.eventitem.event.e_title)
                delta = response.occurrence.starttime.date(
                    ) - self.occurrence.starttime.date()
            elif context['copy_mode'].cleaned_data[
                    'copy_mode'] == "include_parent":
                context['second_title'] = "Create Copied Event at %s: %s" % (
                    context['copy_mode'].cleaned_data[
                        'copy_to_day'].conference.conference_slug,
                    str(context['copy_mode'].cleaned_data['copy_to_day']))
                delta = context['copy_mode'].cleaned_data[
                    'copy_to_day'].day - self.occurrence.starttime.date()
            context['second_form'] = self.make_event_picker(
                request,
                delta)
        elif 'pick_day' in context.keys() and context['pick_day'].is_valid():
            make_copy = True
            context['second_title'] = "Create Copied Event at %s: %s" % (
                context['pick_day'].cleaned_data[
                    'copy_to_day'].conference.conference_slug,
                    str(context['pick_day'].cleaned_data['copy_to_day']))
        return make_copy, context

    def make_event_picker(self, request, delta):
        form = CopyEventForm(request.POST)
        event_choices = ()
        for occurrence in self.children:
            event_choices += ((
                occurrence.pk,
                "%s - %s" % (
                    str(occurrence),
                    (occurrence.start_time + delta).strftime(
                        self.copy_date_format))),)
        form.fields['copied_event'].choices = event_choices
        return form

    def copy_event(self, occurrence, delta, conference, parent_event_id=None):
        gbe_event_copy = occurrence.as_subtype
        gbe_event_copy.pk = None
        gbe_event_copy.event_id = None
        gbe_event_copy.eventitem_ptr_id = None
        gbe_event_copy.eventitem_id = None
        gbe_event_copy.e_conference = conference
        gbe_event_copy.save()
        labels = [conference.conference_slug]
        for label in occurrence.labels:
            if not Conference.objects.filter(conference_slug=label).exists():
                labels += [label]
        response = create_occurrence(
            gbe_event_copy.eventitem_id,
            self.occurrence.starttime + delta,
            max_volunteer=self.occurrence.max_volunteer,
            locations=[self.occurrence.location],
            parent_event_id=parent_event_id,
            labels=labels
        )
        return response

    def copy_events_from_form(self, request):
        form = self.make_event_picker(request, timedelta(0))
        if form.is_valid():
            copied_ids = []
            if form.cleaned_data['copy_mode'] == "copy_children_only":
                response = get_occurrence(
                    form.cleaned_data['target_event'])
                target_event = response.occurrence
                target_day = ConferenceDay.objects.get(
                    day=response.occurrence.starttime.date())
                delta = response.occurrence.starttime.date(
                    ) - self.occurrence.starttime.date()
                conference = response.occurrence.eventitem.event.e_conference
                parent_event_id = response.occurrence.pk
            elif form.cleaned_data['copy_mode'] == "include_parent":
                target_day = form.cleaned_data['copy_to_day']
                delta = target_day.day - self.occurrence.starttime.date()
                conference = form.cleaned_data['copy_to_day'].conference
                response = self.copy_event(
                    self.occurrence,
                    delta,
                    form.cleaned_data['copy_to_day'].conference)
                show_scheduling_occurrence_status(
                    request,
                    response,
                    self.__class__.__name__)
                if response.occurrence:
                    copied_ids += [response.occurrence.pk]
                    parent_event_id = response.occurrence.pk

            for sub_event_id in form.cleaned_data["copied_event"]:
                response = get_occurrence(sub_event_id)
                response = self.copy_event(
                    response.occurrence,
                    delta,
                    conference,
                    parent_event_id)
                show_scheduling_occurrence_status(
                    request,
                    response,
                    self.__class__.__name__)
                if response.occurrence:
                    copied_ids += [response.occurrence.pk]
            if len(copied_ids) > 0:
                return HttpResponseRedirect(
                    "%s?%s-day=%d&filter=Filter&new=%s" % (
                        reverse('manage_event_list',
                                urlconf='gbe.scheduling.urls',
                                args=[conference.conference_slug]),
                        conference.conference_slug,
                        target_day.pk,
                        str(copied_ids),))
        else:
            context = self.build_mode_form(request)
            make_copy, context = self.validate_and_proceed(request, context)
            context['second_form'] = form
            return render(request, self.template, context)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return self.make_context(request)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        context = {}
        if 'pick_mode' in request.POST.keys():
            context = self.build_mode_form(request)
            make_copy, context = self.validate_and_proceed(request, context)
            if make_copy:
                target_day = context['pick_day'].cleaned_data[
                    'copy_to_day']
                delta = target_day.day - self.occurrence.starttime.date()
                response = self.copy_event(
                    self.occurrence,
                    delta,
                    target_day.conference)
                show_scheduling_occurrence_status(
                    request,
                    response,
                    self.__class__.__name__)
                if response.occurrence:
                    slug = target_day.conference.conference_slug
                    return HttpResponseRedirect(
                        "%s?%s-day=%d&filter=Filter&new=%s" % (
                            reverse('manage_event_list',
                                    urlconf='gbe.scheduling.urls',
                                    args=[slug]),
                            slug,
                            target_day.pk,
                            str([response.occurrence.pk]),))
        if 'pick_event' in request.POST.keys():
            return self.copy_events_from_form(request)
        return render(
            request,
            self.template,
            context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CopyOccurrenceView, self).dispatch(*args, **kwargs)
