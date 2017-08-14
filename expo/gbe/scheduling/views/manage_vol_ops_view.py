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
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    update_occurrence,
)
from scheduler.views.functions import (
    get_event_display_info,
)
from scheduler.views import (
    get_manage_opportunity_forms,
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
from gbe.scheduling.views import MakeOccurrenceView
from gbe.scheduling.forms import VolunteerOpportunityForm


class ManageVolOps(MakeOccurrenceView):

    form = None
    permissions = ('Volunteer Coordinator',)

    @never_cache
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('edit_event_schedule',
                                    urlconf='gbe.scheduling.urls',
                                    args=[kwargs['event_type'],
                                          kwargs['eventitem_id'],
                                          kwargs['parent_event_id']]))

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.create = False
        success_url = None

        if 'create' in request.POST.keys() or 'duplicate' in request.POST.keys():
            self.create = True
            if 'create' in request.POST.keys():
                self.event_form = VolunteerOpportunityForm(
                    request.POST,
                    prefix='new_opp',
                    conference=self.item.get_conference())
            else:
                self.event_form = VolunteerOpportunityForm(
                    request.POST,
                    conference=self.item.get_conference())
            if form.is_valid():
                data = self.get_basic_form_settings()

                self.event.type = "Volunteer"
                self.event.e_conference = self.item.get_conference()
                self.event.save()
                response = create_occurrence(
                    self.event.eventitem_id,
                    self.start_time,
                    self.max_volunteer,
                    people=[],
                    locations=[self.room],
                    labels=self.labels,
                    parent=self.item)
                success_url = reverse('edit_event_schedule',
                                      urlconf='gbe.scheduling.urls',
                                      args=[self.event_type,
                                            self.item.eventitem_id,
                                            int(kwargs['parent_event_id'])])
        elif 'edit' in request.POST.keys():
            self.event = get_object_or_404(
                GenericEvent,
                event_id=request.POST['opp_event_id'])
            self.event_form = VolunteerOpportunityForm(
                request.POST,
                instance=self.event)
            if form.is_valid():
                data = self.get_basic_form_settings()
                self.event_form.save()
                response = update_occurrence(
                    int(kwargs['opp_sched_id']),
                    self.start_time,
                    self.max_volunteer,
                    people=[],
                    locations=[self.room])
                success_url = reverse('edit_event_schedule',
                                      urlconf='gbe.scheduling.urls',
                                      args=[self.event_type,
                                            self.item.eventitem_id,
                                            int(kwargs['parent_event_id'])])


        opp_event.save()
        changed_event = opp_event


    elif 'delete' in request.POST.keys():
        opp = get_object_or_404(GenericEvent,
                                event_id=request.POST['opp_event_id'])
        opp.delete()


    elif 'allocate' in request.POST.keys():
        opp_event = Event.objects.get(id=request.POST['opp_sched_id'])
        return HttpResponseRedirect(reverse('edit_event_schedule',
                                            urlconf='gbe.scheduling.urls',
                                    args=['GenericEvent',
                                          opp_event.eventitem.pk,
                                          request.POST['opp_sched_id']]))
    if changed_event:
        return HttpResponseRedirect("%s?changed_id=%d" % (
            reverse('edit_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=[event.event_type_name, event.eventitem.pk, event_id]
                    ),
            changed_event.pk))
    else:
        return HttpResponseRedirect(reverse(
            'edit_event_schedule', urlconf='gbe.scheduling.urls', args=[
                event.event_type_name, event.eventitem.pk, event_id]))


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageVolOps, self).dispatch(*args, **kwargs)
