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
from gbe.scheduling.views import EventWizardView


class ClassWizardView(EventWizardView):
    @never_cache
    def get(self, request, *args, **kwargs):
        raise Exception('made it')
        context = self.groundwork(request, args, kwargs)
        context['next_form'] = True
        context['next_title'] = "Pick the Class"
        return render(request, self.template, context)
