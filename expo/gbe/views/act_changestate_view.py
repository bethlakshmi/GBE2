from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from expo.gbe_logging import log_func
from gbe.functions import validate_perms
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


@login_required
@log_func
def ActChangeStateView(request, bid_id):
    '''
    Fairly specific to act - removes the act from all shows, and resets
    the act to the selected show (if accepted/waitlisted), and then does
    the regular state change
    NOTE: only call on a post request
    BB - I'd like to refactor this to be the same as volunteer form, but
    not right now - 2015?
    '''

    @log_func
    def act_accepted(request):
        return (request.POST['show'] and
                request.POST['accepted'] in ('3', '2'))

    reviewer = validate_perms(request, ('Act Coordinator',))
    if request.method == 'POST':
        act = get_object_or_404(Act, id=bid_id)

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
    return BidChangeStateView(request, bid_id, 'act_review_list')
