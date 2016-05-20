from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.forms import (
    BidEvaluationForm,
    BidStateChangeForm,
    PersonaForm,
    ClassBidForm,
    ParticipantForm,

)
from gbe.models import (
    Class,
    BidEvaluation,
)
from gbe.functions import (
    validate_perms,
    get_conf,
)


@login_required
@log_func
def ReviewClassView(request, class_id):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    If user is not a reviewer, politely decline to show anything.
    '''
    reviewer = validate_perms(request, ('Class Reviewers',))
    aclass = get_object_or_404(
        Class,
        id=class_id,
    )
    if not aclass.is_current:
        return HttpResponseRedirect(
            reverse('class_view', urlconf='gbe.urls', args=[class_id]))
    conference, old_bid = get_conf(aclass)
    classform = ClassBidForm(instance=aclass, prefix='The Class')
    teacher = PersonaForm(instance=aclass.teacher,
                          prefix='The Teacher(s)')
    contact = ParticipantForm(
        instance=aclass.teacher.performer_profile,
        prefix='Teacher Contact Info',
        initial={
            'email': aclass.teacher.performer_profile.user_object.email,
            'first_name':
                aclass.teacher.performer_profile.user_object.first_name,
            'last_name':
                aclass.teacher.performer_profile.user_object.last_name})

    if validate_perms(request, ('Class Coordinator',), require=False):
        actionform = BidStateChangeForm(instance=aclass)
        actionURL = reverse('class_changestate',
                            urlconf='gbe.urls',
                            args=[aclass.id])
    else:
            actionform = False
            actionURL = False
    '''
    if user has previously reviewed the class, provide their review for update
    '''
    try:
        bid_eval = BidEvaluation.objects.filter(
            bid_id=class_id,
            evaluator_id=reviewer.resourceitem_id)[0]
    except:
        bid_eval = BidEvaluation(evaluator=reviewer,
                                 bid=aclass)

    # show class info and inputs for review
    if request.method == 'POST':
        form = BidEvaluationForm(request.POST,
                                 instance=bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = reviewer
            evaluation.bid = aclass
            evaluation.save()
            return HttpResponseRedirect(reverse('class_review_list',
                                                urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid_review.tmpl',
                          {'readonlyform': [classform, teacher, contact],
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
                      {'readonlyform': [classform, teacher, contact],
                       'reviewer': reviewer,
                       'form': form,
                       'actionform': actionform,
                       'actionURL': actionURL,
                       'conference': conference,
                       'old_bid': old_bid,
                       })
