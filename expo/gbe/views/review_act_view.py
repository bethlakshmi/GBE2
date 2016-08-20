from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from django.forms import ModelChoiceField
from django.http import HttpResponseRedirect

from expo.gbe_logging import log_func
from gbe.models import (
    Act,
    BidEvaluation,
    Show,
)
from gbe.forms import (
    ActEditForm,
    BidEvaluationForm,
    BidStateChangeForm,
    PersonaForm,
)
from gbe.functions import (
    get_conf,
    validate_perms,
)


class ReviewActView(View):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    '''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewActView, self).dispatch(*args, **kwargs)


    def get(self, request, *args, **kwargs):
        reviewer = validate_perms(request, ('Act Reviewers', ))

        act_id = kwargs['act_id']
        act = get_object_or_404(Act,
                                id=act_id)
        if not act.is_current:
            return HttpResponseRedirect(
                reverse('act_view', urlconf='gbe.urls', args=[act_id]))
        conference, old_bid = get_conf(act)
        audio_info = act.tech.audio
        stage_info = act.tech.stage
        actform = ActEditForm(instance=act,
                              prefix='The Act',
                              initial={
                                  'track_title': audio_info.track_title,
                                  'track_artist': audio_info.track_artist,
                                  'track_duration': audio_info.track_duration,
                                  'act_duration': stage_info.act_duration
                              })
        performer = PersonaForm(instance=act.performer,
                                prefix='The Performer(s)')

        if validate_perms(request, ('Act Coordinator',), require=False):
            actionform, actionURL = _create_action_form(act)
        else:
                actionform = False
                actionURL = False

        '''
        if user has previously reviewed the act, provide their review for update
        '''
        bid_eval = BidEvaluation.objects.filter(
            bid_id=act_id,
            evaluator_id=reviewer.resourceitem_id).first()
        if bid_eval is None:
            bid_eval = BidEvaluation(evaluator=reviewer, bid=act)

        # show act info and inputs for review
        if request.method == 'POST':
            form = BidEvaluationForm(request.POST, instance=bid_eval)
            if form.is_valid():
                evaluation = form.save(commit=False)
                evaluation.evaluator = reviewer
                evaluation.bid = act
                evaluation.save()
                return HttpResponseRedirect(reverse('act_review_list',
                                                    urlconf='gbe.urls'))
            else:
                return render(request, 'gbe/bid_review.tmpl',
                              {'readonlyform': [actform, performer],
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
                          {'readonlyform': [actform, performer],
                           'reviewer': reviewer,
                           'form': form,
                           'actionform': actionform,
                           'actionURL': actionURL,
                           'conference': conference,
                           'old_bid': old_bid,
                           })

    def post(self, request, *args, **kwargs):
        act_id = kwargs['act_id']
        reviewer = validate_perms(request, ('Act Reviewers', ))
        act = get_object_or_404(Act,
                                id=act_id)
        if not act.is_current:
            return HttpResponseRedirect(
                reverse('act_view', urlconf='gbe.urls', args=[act_id]))
        conference, old_bid = get_conf(act)
        audio_info = act.tech.audio
        stage_info = act.tech.stage
        actform = ActEditForm(instance=act,
                              prefix='The Act',
                              initial={
                                  'track_title': audio_info.track_title,
                                  'track_artist': audio_info.track_artist,
                                  'track_duration': audio_info.track_duration,
                                  'act_duration': stage_info.act_duration
                              })
        performer = PersonaForm(instance=act.performer,
                                prefix='The Performer(s)')

        if validate_perms(request, ('Act Coordinator',), require=False):
            actionform, actionURL = _create_action_form(act)
        else:
                actionform = False
                actionURL = False

        '''
        if user has previously reviewed the act, provide their review for update
        '''
        bid_eval = BidEvaluation.objects.filter(
            bid_id=act_id,
            evaluator_id=reviewer.resourceitem_id).first()
        if bid_eval is None:
            bid_eval = BidEvaluation(evaluator=reviewer, bid=act)

        # show act info and inputs for review
        if request.method == 'POST':
            form = BidEvaluationForm(request.POST, instance=bid_eval)
            if form.is_valid():
                evaluation = form.save(commit=False)
                evaluation.evaluator = reviewer
                evaluation.bid = act
                evaluation.save()
                return HttpResponseRedirect(reverse('act_review_list',
                                                    urlconf='gbe.urls'))
            else:
                return render(request, 'gbe/bid_review.tmpl',
                              {'readonlyform': [actform, performer],
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
                          {'readonlyform': [actform, performer],
                           'reviewer': reviewer,
                           'form': form,
                           'actionform': actionform,
                           'actionURL': actionURL,
                           'conference': conference,
                           'old_bid': old_bid,
                           })


def _create_action_form(act):
    actionform = BidStateChangeForm(instance=act)
    # This requires that the show be scheduled - seems reasonable in
    # current workflow and lets me order by date.  Also - assumes
    # that shows are only scheduled once
    try:
        start = Show.objects.filter(
            scheduler_events__resources_allocated__resource__actresource___item=act)[0]
    except:
        start = ""
    q = Show.objects.filter(
        conference=act.conference,
        scheduler_events__isnull=False).order_by(
            'scheduler_events__starttime')
    actionform.fields['show'] = ModelChoiceField(
        queryset=q,
        empty_label=None,
        label='Pick a Show',
        initial=start)
    actionURL = reverse('act_changestate',
                        urlconf='gbe.urls',
                        args=[act.id])
    return actionform, actionURL
