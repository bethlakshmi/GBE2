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


class ActChangeStateView(BidChangeStateView):
    '''
    Fairly specific to act - removes the act from all shows, and resets
    the act to the selected show (if accepted/waitlisted), and then does
    the regular state change
    NOTE: only call on a post request
    '''
    object_type = Act
    coordinator_permissions = ('Act Coordinator',)
    redirectURL = 'act_review_list'

    def get_bidder(self):
        self.bidder = self.object.performer.contact

    @log_func
    def act_accepted(request):
        return (request.POST['show'] and
                request.POST['accepted'] in ('3', '2'))

    def bid_state_change(self, request, act):

        # Clear out previous castings, deletes ActResource and
        # ResourceAllocation
        ActResource.objects.filter(_item=act).delete()

        # if the act has been accepted, set the show.
        if act_accepted(request):
            # Cast the act into the show by adding it to the schedule
            # resource time
            show = get_object_or_404(sEvent,
                                     eventitem__event=request.POST['show'])
            casting = ResourceAllocation()
            casting.event = show
            actresource = ActResource(_item=act)
            actresource.save()
            for worker in act.get_performer_profiles():
                conflicts = worker.get_conflicts(show)
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
            request, bid_id)
