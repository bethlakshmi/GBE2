from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render

from expo.gbe_logging import log_func
from gbe.functions import validate_perms
from gbe.models import (
    Act,
    BidEvaluation,
    Conference,
)


@login_required
@log_func
def ReviewActListView(request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews
    '''
    reviewer = validate_perms(request, ('Act Reviewers',))
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()
    try:
        header = Act().bid_review_header
        acts = Act.objects.filter(
            submitted=True,
            b_conference=conference).order_by(
                'accepted',
                'performer')
        review_query = BidEvaluation.objects.filter(
            bid=acts).select_related(
                'evaluator').order_by(
                    'bid',
                    'evaluator')
        rows = []
        for act in acts:
            bid_row = {}
            bid_row['bid'] = act.bid_review_summary
            bid_row['reviews'] = review_query.filter(
                bid=act.id).select_related(
                    'evaluator').order_by(
                        'evaluator')
            bid_row['id'] = act.id
            bid_row['review_url'] = reverse('act_review',
                                            urlconf='gbe.urls',
                                            args=[act.id])
            rows.append(bid_row)
    except IndexError:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    conference_slugs = Conference.all_slugs()
    return render(request, 'gbe/bid_review_list.tmpl',
                  {'header': header,
                   'rows': rows,
                   'return_link': reverse('act_review_list',
                                          urlconf='gbe.urls'),
                   'conference_slugs': conference_slugs,
                   'conference': conference}
                  )
