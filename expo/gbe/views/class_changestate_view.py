from django.contrib.auth.decorators import login_required
from expo.gbe_logging import log_func
from django.shortcuts import get_object_or_404

from gbe.views import BidChangeStateView
from gbe.functions import validate_perms
from gbe.models import Class

@login_required
@log_func
def ClassChangeStateView(request, bid_id):
    '''
    Because classes are scheduleable, if a class is rejected, or
    moved back to nodecision, then the scheduling information is
    removed from the class.
    '''
    reviewer = validate_perms(request, ('Class Coordinator', ))
    if request.method == 'POST':
        thisclass = get_object_or_404(Class, id=bid_id)

        # if the class has been rejected/no decision, clear any schedule items.
        if request.POST['accepted'] in ('0', '1'):
            thisclass.scheduler_events.all().delete()
    return BidChangeStateView(request, bid_id, 'class_review_list')
