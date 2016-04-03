from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.functions import validate_perms
from gbe.models import (
    BidEvaluation,
    Conference,
    Volunteer,
)



def _show_edit(user, volunteer):
    return ('Volunteer Coordinator' in user.profile.privilege_groups and
            volunteer.is_current)


@login_required
@log_func
def ReviewVolunteerListView(request):
    '''
    Show the list of act bids, review results,
    and give a way to update the reviews
    '''
    reviewer = validate_perms(request, ('Volunteer Reviewers',))
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()
    header = Volunteer().bid_review_header
    volunteers = Volunteer.objects.filter(
        submitted=True).filter(
            conference=conference).order_by('accepted')
    review_query = BidEvaluation.objects.filter(
        bid=volunteers).select_related(
        'evaluator'
    ).order_by('bid', 'evaluator')

    rows = []
    for volunteer in volunteers:
        bid_row = {}
        bid_row['bid'] = volunteer.bid_review_summary
        bid_row['reviews'] = review_query.filter(
            bid=volunteer.id
        ).select_related(
            'evaluator'
        ).order_by('evaluator')

        bid_row['id'] = volunteer.id
        bid_row['review_url'] = reverse('volunteer_review',
                                        urlconf='gbe.urls',
                                        args=[volunteer.id])
        if _show_edit(request.user, volunteer):
            bid_row['edit_url'] = reverse('volunteer_edit',
                                          urlconf='gbe.urls',
                                          args=[volunteer.id])
            bid_row['assign_url'] = reverse('volunteer_assign',
                                            urlconf='gbe.urls',
                                            args=[volunteer.id])

        rows.append(bid_row)
    conference_slugs = Conference.all_slugs()
    return render(request, 'gbe/bid_review_list.tmpl',
                  {'header': header, 'rows': rows,
                   'action1_text': 'Review',
                   'action1_link': reverse('volunteer_review_list',
                                           urlconf='gbe.urls'),
                   'return_link': reverse('volunteer_review_list',
                                          urlconf='gbe.urls'),
                   'conference_slugs': conference_slugs,
                   'conference': conference},
                  )
