from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.exceptions import PermissionDenied

from landing_page_view import LandingPageView
from gbe.models import (
    Act,
    Class,
    Vendor,
)


@login_required
def CloneBidView(request, bid_type, bid_id):
    '''
    "Revive" an existing bid for use in the existing conference
    '''
    owner = {'Act': lambda bid: bid.performer.contact,
             'Class': lambda bid: bid.teacher.contact,
             'Vendor': lambda bid: bid.profile}

    if bid_type not in ('Act', 'Class', 'Vendor'):
        raise Http404   # or something
    bid = eval(bid_type).objects.get(pk=bid_id)
    owner_profile = owner[bid_type](bid)
    if request.user.profile != owner_profile:
        raise PermissionDenied
    new_bid = bid.clone()
    return LandingPageView(request)
