from django.contrib.auth.decorators import login_required
from expo.gbe_logging import log_func

from django.shortcuts import (
    render,
    get_object_or_404,
)
from gbe.models import Vendor
from gbe.forms import (
    VendorBidForm,
    ParticipantForm,
)
from gbe.functions import validate_perms


@login_required
@log_func
def ViewVendorView(request, vendor_id):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    If user is not a reviewer, politely decline to show anything.
    '''

    vendor = get_object_or_404(Vendor, id=vendor_id)
    if vendor.profile != request.user.profile:
        validate_perms(request, ('Vendor Reviewers',), require=True)
    vendorform = VendorBidForm(instance=vendor, prefix='The Business')
    profile = ParticipantForm(instance=vendor.profile,
                              initial={'email': request.user.email,
                                       'first_name': request.user.first_name,
                                       'last_name': request.user.last_name},
                              prefix='The Contact Info')

    return render(request, 'gbe/bid_view.tmpl',
                  {'readonlyform': [vendorform, profile]})
