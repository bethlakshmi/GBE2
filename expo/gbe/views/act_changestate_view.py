from django.contrib import messages
from django.shortcuts import get_object_or_404
from expo.gbe_logging import log_func
from scheduler.models import (
    ActResource,
    Event as sEvent,
    ResourceAllocation,
)
from expo.settings import (
    DATETIME_FORMAT,
    DAY_FORMAT,
    )
from django.utils.formats import date_format
from gbe.views import BidChangeStateView
from gbe.models import Act
from gbe.functions import send_bid_state_change_mail


class ActChangeStateView(BidChangeStateView):
    object_type = Act
    coordinator_permissions = ('Act Coordinator',)
    redirectURL = 'act_review_list'
    new_show = None

    def get_bidder(self):
        self.bidder = self.object.performer.contact

    def act_accepted(self, request):
        return (request.POST['show'] and
                request.POST['accepted'] in ('3', '2'))

    @log_func
    def bid_state_change(self, request):
        # Clear out previous castings, deletes ActResource and
        # ResourceAllocation
        ActResource.objects.filter(_item=self.object).delete()

        # if the act has been accepted, set the show.
        if self.act_accepted(request):
            # Cast the act into the show by adding it to the schedule
            # resource time
            casting = ResourceAllocation()
            casting.event = self.new_show
            actresource = ActResource(
                _item=self.object,
                role=request.POST['casting'])
            actresource.save()
            for worker in self.object.get_performer_profiles():
                conflicts = worker.get_conflicts(self.new_show)
                for problem in conflicts:
                    messages.warning(
                        request,
                        "%s is booked for - %s - %s" % (
                            str(worker),
                            str(problem),
                            date_format(problem.starttime, "DATETIME_FORMAT")
                        )
                    )

            casting.resource = actresource
            casting.save()
        return super(ActChangeStateView, self).bid_state_change(
            request)

    def notify_bidder(self, request):
        email_show = None
        if (str(self.object.accepted) != request.POST['accepted']) or (
                request.POST['accepted'] == '3'):
            # only send the show when act is accepted
            if request.POST['accepted'] == '3':
                email_show = self.new_show
            send_bid_state_change_mail(
                str(self.object_type.__name__).lower(),
                self.bidder.contact_email,
                self.bidder.get_badge_name(),
                self.object,
                int(request.POST['accepted']),
                show=email_show)

    def prep_bid(self, request, args, kwargs):
        super(ActChangeStateView, self).prep_bid(request, args, kwargs)
        if self.act_accepted(request):
            self.new_show = get_object_or_404(
                sEvent,
                eventitem__event=request.POST['show'])
