from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from expo.gbe_logging import log_func

from gbe.functions import validate_perms
from gbe.views import BidChangeStateView


@login_required
@log_func
@never_cache
def CostumeChangeStateView(request, bid_id):
    reviewer = validate_perms(request, ('Costume Coordinator',))
    return BidChangeStateView(request, bid_id, 'costume_review_list')
