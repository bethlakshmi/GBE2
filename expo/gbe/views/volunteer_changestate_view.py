from expo.gbe_logging import log_func
from django.shortcuts import (
    get_object_or_404,
)
from gbe.models import Volunteer
from gbe.views import BidChangeStateView
from scheduler.models import Worker, Event
from django.contrib import messages
from gbe.email.functions import send_schedule_update_mail


class VolunteerChangeStateView(BidChangeStateView):
    object_type = Volunteer
    coordinator_permissions = ('Volunteer Coordinator',)
    redirectURL = 'volunteer_review_list'

    def get_bidder(self):
        self.bidder = self.object.profile

    def groundwork(self, request, args, kwargs):
        self.prep_bid(request, args, kwargs)
        if request.POST['accepted'] != '3':
            self.notify_bidder(request)

    @log_func
    def bid_state_change(self, request):
        # Clear all commitments
        Worker.objects.filter(
            _item=self.object.profile,
            role='Volunteer').delete()

        # if the volunteer has been accepted, set the events.
        if request.POST['accepted'] == '3':
            for assigned_event in request.POST.getlist('events'):
                event = get_object_or_404(Event, pk=assigned_event)
                warnings = event.allocate_worker(
                        self.bidder,
                        'Volunteer')
                for warning in warnings:
                    messages.warning(request,
                                     warning)

            email_status = send_schedule_update_mail('Volunteer', self.bidder)
            self.check_email_status(request, email_status)

        return super(VolunteerChangeStateView, self).bid_state_change(
            request)
