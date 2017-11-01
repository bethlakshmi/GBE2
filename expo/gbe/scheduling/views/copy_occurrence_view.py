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
    template = 'gbe/scheduling/event_wizard.tmpl'
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

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return self.make_context(request)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        context = self.build_mode_form(request)
        if context['copy_mode'].is_valid():
            context['second_form'] = True
            context['second_title'] = "Copying %s to ..." % (
                self.occurrence.eventitem.event.e_title)
        return render(
            request,
            self.template,
            context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CopyOccurrenceView, self).dispatch(*args, **kwargs)
