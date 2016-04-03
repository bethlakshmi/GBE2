from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.models import (
    BidEvaluation,
    Class,
    Conference,
)
from gbe.functions import validate_perms

@login_required
@log_func
def ReviewClassListView(request):
    '''
    Show the list of class bids, review results,
    and give a way to update the reviews
    '''

    reviewer = validate_perms(request, ('Class Reviewers', ))
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()
    header = Class().bid_review_header
    classes = Class.objects.filter(
        submitted=True).filter(
            conference=conference).order_by(
            'accepted',
            'title')
    review_query = BidEvaluation.objects.filter(
        bid=classes).select_related(
            'evaluator').order_by('bid',
                                  'evaluator')
    rows = []
    for aclass in classes:
        bid_row = {}
        bid_row['bid'] = aclass.bid_review_summary
        bid_row['reviews'] = review_query.filter(
            bid=aclass.id).select_related(
                'evaluator').order_by('evaluator')
        bid_row['id'] = aclass.id
        bid_row['review_url'] = reverse('class_review',
                                        urlconf='gbe.urls',
                                        args=[aclass.id])
        rows.append(bid_row)
    conference_slugs = Conference.all_slugs()

    return render(request,
                  'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('class_review_list',
                                           urlconf='gbe.urls'),
                   'return_link': reverse('class_review_list',
                                          urlconf='gbe.urls'),
                   'conference_slugs': conference_slugs,
                   'conference': conference}
                  )
