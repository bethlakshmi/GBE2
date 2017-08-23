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
    ScheduleSelectionForm,
    VolunteerOpportunityForm,
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
from scheduler.views import (
    get_worker_allocation_forms,
)
from gbe.scheduling.views.functions import (
    get_single_role,
    get_multi_role,
    get_start_time,
    show_scheduling_occurrence_status,
)
from gbe.models import (
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
from scheduler.forms import WorkerAllocationForm
from gbe_forms_text import (
    rank_interest_options,
)


class ShowCalendarView(View):
    template = 'gbe/scheduling/calendar.tmpl'

    def groundwork(self, request, args, kwargs):
        pass

    def get(self, request, *args, **kwargs):
        context = {}
        if "calendar_type" in kwargs:
            calendar_type = int(kwargs['calendar_type'])
        if "conference" in kwargs:
            conf_slug = int(kwargs['conference'])
        if "day" in kwargs:
            day = int(kwargs['day'])

        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ShowCalendarView, self).dispatch(*args, **kwargs)
