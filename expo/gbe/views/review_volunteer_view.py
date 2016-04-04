from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.functions import (
    validate_perms,
    get_conf,
)
from gbe.models import (
    BidEvaluation,
    Conference,
)
from gbe.forms import (
    BidEvaluationForm,
    BidStateChangeForm,
    ParticipantForm,
    VolunteerBidForm,
)
from gbe.models import Volunteer


@login_required
@log_func
def ReviewVolunteerView(request, volunteer_id):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    If user is not a reviewer, politely decline to show anything.
    '''
    reviewer = validate_perms(request, ('Volunteer Reviewers',))
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()

    if int(volunteer_id) == 0 and request.method == 'POST':
        volunteer_id = int(request.POST['volunteer'])
    volunteer = get_object_or_404(
        Volunteer,
        id=volunteer_id,
    )
    if not volunteer.is_current:
        return view_volunteer(request, volunteer_id)
    conference, old_bid = get_conf(volunteer)
    volunteer_prof = volunteer.profile
    volform = VolunteerBidForm(
        instance=volunteer,
        prefix='The Volunteer',
        available_windows=volunteer.conference.windows(),
        unavailable_windows=volunteer.conference.windows())
    profile = ParticipantForm(
        instance=volunteer_prof,
        initial={'email': volunteer_prof.user_object.email,
                 'first_name': volunteer_prof.user_object.first_name,
                 'last_name': volunteer_prof.user_object.last_name},
        prefix='Contact Info')
    if 'Volunteer Coordinator' in request.user.profile.privilege_groups:
        actionform = BidStateChangeForm(instance=volunteer)
        actionURL = reverse('volunteer_changestate',
                            urlconf='gbe.urls',
                            args=[volunteer_id])
    else:
        actionform = False
        actionURL = False
    '''
    if user has previously reviewed the bid, provide his review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(
            bid_id=volunteer_id,
            evaluator_id=reviewer.resourceitem_id)[0]
    except:
        bid_eval = BidEvaluation(evaluator=reviewer, bid=volunteer)
    # show info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST,
                                 instance=bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = volunteer
            evaluation.save()
            return HttpResponseRedirect(reverse('volunteer_review_list',
                                                urlconf='gbe.urls'))
        else:
            return render(request, 'gbe/bid_review.tmpl',
                          {'readonlyform': [volform],
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
                      {'readonlyform': [volform, profile],
                       'reviewer': reviewer,
                       'form': form,
                       'actionform': actionform,
                       'actionURL': actionURL,
                       'conference': conference,
                       'old_bid': old_bid,
                       })
