from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.models import (
    BidEvaluation,
    Conference,
    Vendor,
)
from gbe.functions import validate_perms


@login_required
@log_func
def ReviewVendorListView(request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews
    '''
    reviewer = validate_perms(request, ('Vendor Reviewers',))
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()
    header = Vendor().bid_review_header
    vendors = Vendor.objects.filter(
        submitted=True).filter(
            b_conference=conference).order_by(
                'accepted',
                'b_title')
    review_query = BidEvaluation.objects.filter(
        bid=vendors).select_related(
            'evaluator').order_by('bid',
                                  'evaluator')
    rows = []
    for vendor in vendors:
        bid_row = {}
        bid_row['bid'] = vendor.bid_review_summary
        bid_row['reviews'] = review_query.filter(
            bid=vendor.id).select_related(
                'evaluator').order_by('evaluator')
        bid_row['id'] = vendor.id
        bid_row['review_url'] = reverse('vendor_review',
                                        urlconf='gbe.urls',
                                        args=[vendor.id])
        rows.append(bid_row)
    conference_slugs = Conference.all_slugs()
    return render(request, 'gbe/bid_review_list.tmpl',
                  {'header': header,
                   'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('vendor_review_list',
                                           urlconf='gbe.urls'),
                   'return_link': reverse('vendor_review_list',
                                          urlconf='gbe.urls'),
                   'conference_slugs': conference_slugs,
                   'conference': conference}
                  )
