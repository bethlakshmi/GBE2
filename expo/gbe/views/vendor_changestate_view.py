from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from expo.gbe_logging import log_func

from gbe.functions import validate_perms
from gbe.views import BidChangeStateView


@login_required
@log_func
@never_cache
def VendorChangeStateView(request, bid_id):
    '''
    The generic function to change a bid to a new state (accepted,
    rejected, etc.).  This can work for any Biddable class, but may
    be an add-on to other work for a given class type.
    NOTE: only call on a post request
    '''
    reviewer = validate_perms(request, ('Vendor Coordinator',))
    return BidChangeStateView(request, bid_id, 'vendor_review_list')
