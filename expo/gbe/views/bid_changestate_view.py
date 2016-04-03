from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from expo.gbe_logging import log_func
from gbe.models import Biddable
from gbe.forms import BidStateChangeForm

@login_required
@log_func
def BidChangeStateView(request, bid_id, redirectURL):
    '''
    The generic function to change a bid to a new state (accepted,
    rejected, etc.). This can work for any Biddable class, but may
    be an add-on to other work for a given class type.
    NOTE: only call on a post request, and call from within a specific
    type of bid changestate function
    '''
    bid = get_object_or_404(Biddable, id=bid_id)

    # show class info and inputs for review
    if request.method == 'POST':
        form = BidStateChangeForm(request.POST, instance=bid)
        if form.is_valid():
            bid = form.save()
            return HttpResponseRedirect(reverse(redirectURL,
                                                urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid_review.tmpl',
                          {'actionform': False,
                           'actionURL': False})

    return HttpResponseRedirect(reverse(redirectURL, urlconf='gbe.urls'))
