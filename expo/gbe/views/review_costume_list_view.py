from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.models import (
    Conference,
    Costume,
    BidEvaluation,
)
from gbe.functions import validate_perms


@login_required
@log_func
def ReviewCostumeListView(request):
    '''
    Show the list of costume bids, review results,
    and give a way to update the reviews
    '''

    reviewer = validate_perms(request, ('Costume Reviewers', ))
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()
    header = Costume().bid_review_header
    costumes = Costume.objects.filter(
        submitted=True).filter(
            b_conference=conference).order_by(
                'accepted',
                'b_title')
    review_query = BidEvaluation.objects.filter(
        bid=costumes).select_related(
        'evaluator').order_by('bid',
                              'evaluator')
    rows = []
    for acostume in costumes:
        bid_row = {}
        bid_row['bid'] = acostume.bid_review_summary
        bid_row['reviews'] = review_query.filter(
            bid=acostume.id).select_related(
                'evaluator').order_by('evaluator')
        bid_row['id'] = acostume.id
        bid_row['review_url'] = reverse('costume_review',
                                        urlconf='gbe.urls',
                                        args=[acostume.id])
        rows.append(bid_row)
    conference_slugs = Conference.all_slugs()

    return render(request,
                  'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('costume_review_list',
                                           urlconf='gbe.urls'),
                   'return_link': reverse('costume_review_list',
                                          urlconf='gbe.urls'),
                   'conference_slugs': conference_slugs,
                   'conference': conference}
                  )
