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
    show_scheduling_occurrence_status,
)
from gbe.models import (
    ConferenceDay,
    Event,
)
from gbe.functions import validate_perms
from gbe.duration import Duration
from gbe.views.class_display_functions import get_scheduling_info
from expo.settings import DATETIME_FORMAT


class CopyOccurrenceView(View):
    template = 'gbe/scheduling/copy_wizard.tmpl'
    permissions = ('Scheduling Mavens',)

    occurrence = None
    children = []
    future_days = None

    def groundwork(self, request, args, kwargs):
        self.occurrence_id = kwargs['occurrence_id']
        self.profile = validate_perms(request, self.permissions)
        response = get_occurrence(self.occurrence_id)
        self.occurrence = response.occurrence
        response = get_occurrences(parent_event_id=self.occurrence_id)
        self.children = response.occurrences

    def make_context(self, request):
        context = {
            'first_title': "Copying - %s" % self.occurrence.eventitem.event.e_title}
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
            'first_title': "Copying - %s" % self.occurrence.eventitem.event.e_title}
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
            elif context['copy_mode'].cleaned_data[
                    'copy_mode'] == "include_parent":
                context['second_title'] = "Create Copied Event at %s: %s" % (
                    context['copy_mode'].cleaned_data[
                        'copy_to_day'].conference.conference_slug,
                    str(context['copy_mode'].cleaned_data['copy_to_day']))
            context['second_form'] = self.make_event_picker(
                request,
                (context['copy_mode'].cleaned_data[
                    'copy_mode'] == "include_parent"))
        elif 'pick_day' in context.keys() and context['pick_day'].is_valid():
            make_copy = True
            context['second_title'] = "Create Copied Event at %s: %s" % (
                context['pick_day'].cleaned_data[
                    'copy_to_day'].conference.conference_slug,
                    str(context['pick_day'].cleaned_data['copy_to_day']))
        return make_copy, context

    def make_event_picker(self, request, copy_parent):
        form = CopyEventForm(request.POST)
        event_choices = ()
        if copy_parent:
           event_choices = ((
            self.occurrence.pk,
            "%s - %s" % (
                str(self.occurrence),
                self.occurrence.start_time.strftime(DATETIME_FORMAT))),)
        for occurrence in self.children:
            event_choices += ((
                occurrence.pk,
                "%s - %s" % (
                    str(occurrence),
                    occurrence.start_time.strftime(DATETIME_FORMAT))),)
        form.fields['copied_event'].choices = event_choices
        return form

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
        return render(
            request,
            self.template,
            context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CopyOccurrenceView, self).dispatch(*args, **kwargs)
