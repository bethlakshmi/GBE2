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
    CopyEventPickDayForm,
    CopyEventPickModeForm,
)
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    get_occurrences,
    update_occurrence,
)
from gbe.scheduling.views.functions import (
    get_single_role,
    get_multi_role,
    get_start_time,
    show_scheduling_occurrence_status,
)
from gbe.models import (
    ConferenceDay,
    Event,
)
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
    validate_perms
)
from gbe.duration import Duration
from gbe.views.class_display_functions import get_scheduling_info
from gbe_forms_text import (
    rank_interest_options,
)


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

    def validate_and_proceed(self, context):
        initial = {}
        if 'copy_mode' in context.keys() and context['copy_mode'].is_valid():
            context['second_form'] = True
            if context['copy_mode'].cleaned_data[
                    'copy_mode'] == "copy_children_only":
                context['second_title'] = "Destination is %s: %s" % (
                    context['copy_mode'].cleaned_data[
                        'target_event'].e_conference.conference_slug,
                    context['copy_mode'].cleaned_data['target_event'].e_title)
                initial = {
                    'conference': context['copy_mode'].cleaned_data[
                        'target_event'].e_conference,
                    'new_parent': context['copy_mode'].cleaned_data['target_event'],
                }
            elif context['copy_mode'].cleaned_data[
                    'copy_mode'] == "include_parent":
                context['second_title'] = "Create Copied Event at %s: %s" % (
                    context['copy_mode'].cleaned_data[
                        'copy_to_day'].conference.conference_slug,
                    str(context['copy_mode'].cleaned_data['copy_to_day']))
                initial = {
                    'conference': context['copy_mode'].cleaned_data[
                        'copy_to_day'].conference,
                    'day': context['copy_mode'].cleaned_data['copy_to_day'],
                    'include_parent': True,
                }
        elif 'pick_day' in context.keys() and context['pick_day'].is_valid():
            context['second_form'] = True
            context['second_title'] = "Create Copied Event at %s: %s" % (
                context['pick_day'].cleaned_data[
                    'copy_to_day'].conference.conference_slug,
                    str(context['pick_day'].cleaned_data['copy_to_day']))
            initial = {
                'conference': context['pick_day'].cleaned_data[
                        'copy_to_day'].conference,
                'day': context['pick_day'].cleaned_data['copy_to_day'],
                'include_parent': True,
            }
        return initial, context

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return self.make_context(request)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if 'pick_event' in request.POST.keys():
            context = self.build_mode_form(request)
            initial, context = self.validate_and_proceed(context)
        return render(
            request,
            self.template,
            context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CopyOccurrenceView, self).dispatch(*args, **kwargs)
