from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    update_occurrence,
)
from gbe.models import (
    Event,
    Room,
)
from gbe.scheduling.views import MakeOccurrenceView
from gbe.scheduling.forms import VolunteerOpportunityForm


class ManageVolOps(MakeOccurrenceView):

    permissions = ('Volunteer Coordinator',)

    @never_cache
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('edit_event_schedule',
                                    urlconf='gbe.scheduling.urls',
                                    args=[kwargs['event_type'],
                                          kwargs['eventitem_id'],
                                          kwargs['parent_event_id']]))

    def make_post_response(self, request, response=None):
        self.success_url = reverse('edit_event_schedule',
                                      urlconf='gbe.scheduling.urls',
                                      args=[self.event_type,
                                            self.item.eventitem_id,
                                            int(kwargs['parent_event_id'])])
        if response and response.occurrence:
            self.success_url = "%s?changed_id=%d" % (
                self.success_url,
                response.occurrence.pk)
        return super(ManageVolOps, self).make_post_response(request, response)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.create = False
        response = None

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
            return self.make_post_response(request, response)
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
            return self.make_post_response(request, response)
        elif 'delete' in request.POST.keys():
            opp = get_object_or_404(GenericEvent,
                                event_id=request.POST['opp_event_id'])
            opp.delete()
        elif 'allocate' in request.POST.keys():
            opp_event = get_occurrence(id=request.POST['opp_sched_id'])
            return HttpResponseRedirect(
                reverse('edit_event_schedule',
                        urlconf='gbe.scheduling.urls',
                        args=['GenericEvent',
                              opp_event.eventitem.pk,
                              request.POST['opp_sched_id']]))
