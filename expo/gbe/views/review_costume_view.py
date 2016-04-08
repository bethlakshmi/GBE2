from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import (
    render,
    get_object_or_404,
)

from expo.gbe_logging import log_func
from gbe.functions import (
    validate_perms,
    get_conf,
)
from gbe.forms import (
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
    ParticipantForm,
    PersonaForm,
    BidStateChangeForm,
    BidEvaluationForm,
)
from gbe.models import (
    BidEvaluation,
    Costume,
)


@login_required
@log_func
def ReviewCostumeView(request, costume_id):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    If user is not a reviewer, politely decline to show anything.
    '''
    reviewer = validate_perms(request, ('Costume Reviewers', ))
    costume = get_object_or_404(
        Costume,
        id=costume_id
    )
    if not costume.is_current:
        return view_costume(request, costume_id)
    conference, old_bid = get_conf(costume)
    costume_form = CostumeBidSubmitForm(instance=costume,
                                        prefix='Costume Proposal')
    details = CostumeDetailsSubmitForm(instance=costume)

    performer = PersonaForm(instance=costume.performer,
                            prefix='The Performer')

    profile = ParticipantForm(
        instance=costume.profile,
        prefix='The Owner',
        initial={
            'email': costume.profile.user_object.email,
            'first_name': costume.profile.user_object.first_name,
            'last_name': costume.profile.user_object.last_name})

    if validate_perms(request, ('Costume Coordinator',), require=False):
        actionform = BidStateChangeForm(instance=costume)
        actionURL = reverse('costume_changestate',
                            urlconf='gbe.urls',
                            args=[costume_id])
    else:
            actionform = False
            actionURL = False

    '''
    if user has previously reviewed the act, provide their review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(
            bid_id=costume_id,
            evaluator_id=reviewer.resourceitem_id)[0]
    except:
        bid_eval = BidEvaluation(evaluator=reviewer, bid=costume)

    # show costume info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST, instance=bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = costume
            evaluation.save()
            return HttpResponseRedirect(reverse('costume_review_list',
                                                urlconf='gbe.urls'))
        else:
            return render(request, 'gbe/bid_review.tmpl',
                          {'readonlyform': [
                                costume_form,
                                details,
                                performer,
                                profile],
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
                      {'readonlyform': [
                            costume_form,
                            details,
                            performer,
                            profile],
                       'reviewer': reviewer,
                       'form': form,
                       'actionform': actionform,
                       'actionURL': actionURL,
                       'conference': conference,
                       'old_bid': old_bid,
                       })
