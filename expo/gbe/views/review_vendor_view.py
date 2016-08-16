from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)

from expo.gbe_logging import log_func
from gbe.models import (
    BidEvaluation,
    Vendor,
)
from gbe.forms import (
    BidEvaluationForm,
    BidStateChangeForm,
    VendorBidForm,
)
from gbe.functions import (
    get_conf,
    validate_perms,
)


@login_required
@log_func
def ReviewVendorView(request, vendor_id):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    If user is not a reviewer, politely decline to show anything.
    '''
    reviewer = validate_perms(request, ('Vendor Reviewers',))
    vendor = get_object_or_404(
        Vendor,
        id=vendor_id,
    )
    if not vendor.is_current:
        return HttpResponseRedirect(
            reverse('vendor_view', urlconf='gbe.urls', args=[vendor_id]))
    conference, old_bid = get_conf(vendor)
    volform = VendorBidForm(instance=vendor, prefix='The Vendor')
    if validate_perms(request, ('Vendor Coordinator'), require=False):
        actionform = BidStateChangeForm(instance=vendor)
        actionURL = reverse('vendor_changestate',
                            urlconf='gbe.urls',
                            args=[vendor_id])
    else:
            actionform = False
            actionURL = False

    '''
    if user has previously reviewed the act, provide his review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(
            bid_id=vendor_id,
            evaluator_id=reviewer.resourceitem_id)[0]
    except:
        bid_eval = BidEvaluation(evaluator=reviewer, bid=vendor)
    # show act info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST, instance=bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = vendor
            evaluation.save()
            return HttpResponseRedirect(reverse('vendor_review_list',
                                                urlconf='gbe.urls'))
        else:
            return render(request, 'gbe/bid_review.tmpl',
                          {'readonlyform': [volform],
                           'reviewer': reviewer,
                           'form': form,
                           'actionform': actionform,
                           'actionURL': actionURL,
                           'conference': conference,
                           'old_bid': old_bid,
                           })
    else:
        form = BidEvaluationForm(instance=bid_eval)
        return render(request,
                      'gbe/bid_review.tmpl',
                      {'readonlyform': [volform],
                       'reviewer': reviewer,
                       'form': form,
                       'actionform': actionform,
                       'actionURL': actionURL,
                       'conference': conference,
                       'old_bid': old_bid,
                       })
