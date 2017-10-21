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
    PickEventForm,
    ScheduleSelectionForm,
    VolunteerOpportunityForm,
    WorkerAllocationForm,
)
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    get_occurrences,
    update_occurrence,
)
from scheduler.views.functions import (
    get_event_display_info,
)
from gbe.scheduling.views.functions import (
    get_single_role,
    get_multi_role,
    get_start_time,
    show_scheduling_occurrence_status,
)
from gbe.models import (
    Conference,
    Event,
    Performer,
    Profile,
    Room,
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


class EventWizardView(View):
    template = 'gbe/scheduling/event_wizard.tmpl'
    permissions = ('Scheduling Mavens',)

    role_key = {
        'Staff Lead': 'staff_lead',
        'Moderator': 'moderator',
        'Teacher': 'teacher',
    }

    role_class = {
        'Staff Lead': 'Profile',
        'Moderator': 'Performer',
        'Teacher': 'Performer',
    }
    occurrence = None
    people = []
    event_form = None

    def get_pick_event_form(self, request):
        if 'pick_event' in request.GET.keys():
            return PickEventForm(request.GET)
        else:
            return PickEventForm()

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        if "conference" in kwargs:
            self.conference = get_object_or_404(
                Conference,
                conference_slug=kwargs['conference'])
        context = {
            'selection_form':  self.get_pick_event_form(request),
        }
        return context

    @never_cache
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        if 'pick_event' in request.GET.keys() and context[
                'selection_form'].is_valid():
            if context['selection_form'].cleaned_data['event_type'] == 'conference':
                return HttpResponseRedirect(
                    reverse('create_class_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]))
        return render(request, self.template, context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventWizardView, self).dispatch(*args, **kwargs)
