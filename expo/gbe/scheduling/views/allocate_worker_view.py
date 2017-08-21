from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from scheduler.idd import (
    set_person,
    test_booking,
)
from scheduler.data_transfer import (
    Error,
    GeneralResponse,
    Person,
)
from gbe.scheduling.views import MakeOccurrenceView
from gbe.scheduling.forms import WorkerAllocationForm
from gbe.scheduling.views.functions import get_single_role
from gbe.functions import send_schedule_update_mail


class AllocateWorkerView(MakeOccurrenceView):

    permissions = ('Volunteer Coordinator',)

    @never_cache
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('edit_event_schedule',
                                    urlconf='gbe.scheduling.urls',
                                    args=[kwargs['event_type'],
                                          kwargs['eventitem_id'],
                                          kwargs['parent_event_id']]))

    def make_post_response(self,
                           request,
                           response=None,
                           occurrence_id=None,
                           errorcontext=None):
        self.success_url = reverse('edit_event_schedule',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.event_type,
                                         self.item.eventitem_id,
                                         occurrence_id])
        if response and response.booking_id:
            self.success_url = "%s?changed_id=%d" % (
                self.success_url,
                response.booking_id)
        return super(AllocateWorkerView, self).make_post_response(
            request,
            response,
            occurrence_id,
            errorcontext)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        form = WorkerAllocationForm(request.POST)
        response = None
        occurrence_id = None
        if "occurrence_id" in kwargs:
            occurrence_id = int(kwargs['occurrence_id'])

        if 'delete' in request.POST.keys():
            '''
            alloc = ResourceAllocation.objects.get(id=request.POST['alloc_id'])
            res = alloc.resource
            profile = res.as_subtype.workeritem
            alloc.delete()
            res.delete()
            '''
            # This delete looks dangerous, considering that Event.allocate_worker
            # seems to allow us to create multiple allocations for the same Worker
            send_schedule_update_mail("Volunteer", profile)

        elif not form.is_valid():
            context = None
            if request.POST['alloc_id'] == '-1':
                form.data['alloc_id'] = -1
                context = {'new_worker_alloc_form': form}
            else:
                is_present = test_booking(request.POST['alloc_id'], self.occurence_id)
                if not is_present:
                    response = GeneralResponse(errors=[Error(
                        code="BOOKING_NOT_FOUND",
                        details="Could not find booking id %s for occurrence id %s." % (
                            request.POST['alloc_id'], self.occurence_id)), ])
                context = {'worker_alloc_forms': form}
            return self.make_post_response(request,
                                           response=response,
                                           occurrence_id=occurrence_id,
                                           errorcontext=context) 
        else:
            data = form.cleaned_data
            if data.get('worker', None):
                if data['role'] == "Volunteer":
                    data['worker'].workeritem.as_subtype.check_vol_bid(
                        self.item.e_conference)
                person = Person(
                    user=data['worker'].workeritem.as_subtype.user_object,
                    public_id=data['worker'].workeritem.as_subtype.pk,
                    role=data['role'],
                    label=data['label'],
                    worker=None)
                if int(data['alloc_id']) > -1:
                    person.booking_id = int(data['alloc_id'])
                response = set_person(
                    occurrence_id,
                    person
                )
                send_schedule_update_mail("Volunteer", data['worker'])
        return HttpResponseRedirect(
            reverse('edit_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=[self.event_type,
                          self.item.eventitem_id,
                          occurrence_id]))
