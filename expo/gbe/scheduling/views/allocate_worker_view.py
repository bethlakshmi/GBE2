from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from scheduler.idd import (
    remove_booking,
    set_person,
    test_booking,
)
from scheduler.data_transfer import (
    Error,
    PersonResponse,
    Person,
)
from gbe.scheduling.views import MakeOccurrenceView
from gbe.scheduling.forms import WorkerAllocationForm
from gbe.scheduling.views.functions import get_single_role
from gbe.email.functions import send_schedule_update_mail
from gbe.scheduling.views.functions import show_scheduling_booking_status
from gbetext import volunteer_allocate_email_fail_msg
from django.contrib import messages
from gbe.models import UserMessage


class AllocateWorkerView(MakeOccurrenceView):

    permissions = ('Volunteer Coordinator',)

    @never_cache
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('edit_event_schedule',
                                    urlconf='gbe.scheduling.urls',
                                    args=[kwargs['event_type'],
                                          kwargs['eventitem_id'],
                                          kwargs['occurrence_id']]))

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
        if response:
            show_scheduling_booking_status(
                request,
                response,
                self.__class__.__name__)
            if response.booking_id:
                self.success_url = "%s?changed_id=%d" % (
                    self.success_url,
                    response.booking_id)
                return HttpResponseRedirect(self.success_url)
        return self.make_context(request, occurrence_id, errorcontext)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        form = WorkerAllocationForm(request.POST)
        response = None
        occurrence_id = None
        email_status = None
        if "occurrence_id" in kwargs:
            occurrence_id = int(kwargs['occurrence_id'])
        if not form.is_valid():
            context = None
            if request.POST['alloc_id'] == '-1':
                form.data['alloc_id'] = -1
                context = {'new_worker_alloc_form': form}
            else:
                is_present = test_booking(
                    int(request.POST['alloc_id']), occurrence_id)
                if not is_present:
                    response = PersonResponse(errors=[Error(
                        code="BOOKING_NOT_FOUND",
                        details="Booking id %s for occurrence %d not found" % (
                            request.POST['alloc_id'], occurrence_id)), ])
                context = {'worker_alloc_forms': form}
            return self.make_post_response(request,
                                           response=response,
                                           occurrence_id=occurrence_id,
                                           errorcontext=context)
        else:
            data = form.cleaned_data
            if 'delete' in request.POST.keys():
                if ('alloc_id' not in request.POST) or (len(
                        request.POST['alloc_id']) == 0):
                    return self.make_post_response(
                        request,
                        PersonResponse(errors=[Error(
                            code="NO_BOOKING",
                            details="No booking id for occurrence id %d." % (
                                occurrence_id))]), occurrence_id)
                response = remove_booking(
                    occurrence_id,
                    booking_id=int(request.POST['alloc_id']))
                if response.booking_id:
                    email_status = send_schedule_update_mail(
                        "Volunteer", data['worker'].workeritem.as_subtype)
            elif data.get('worker', None):
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
                email_status = send_schedule_update_mail("Volunteer",
                                                         data['worker'])
            if email_status:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="EMAIL_FAILURE",
                    defaults={
                        'summary': "Email Failed",
                        'description': volunteer_allocate_email_fail_msg})
                messages.error(
                    request,
                    user_message[0].description)
            self.success_url = reverse('edit_event_schedule',
                                       urlconf='gbe.scheduling.urls',
                                       args=[self.event_type,
                                             self.item.eventitem_id,
                                             occurrence_id])
        return self.make_post_response(request,
                                       response=response,
                                       occurrence_id=occurrence_id)
