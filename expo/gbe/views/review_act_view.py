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


    def groundwork(self, request, args, kwargs):
        self.act_id = kwargs['act_id']
        self.act = get_object_or_404(Act,
                                     id=self.act_id)
        self.reviewer = validate_perms(request, ('Act Reviewers', ))
        self.conference, self.old_bid = get_conf(self.act)
        self.audio_info = self.act.tech.audio
        self.stage_info = self.act.tech.stage
        self.actform = ActEditForm(instance=self.act,
                              prefix='The Act',
                              initial={
                                  'track_title': self.audio_info.track_title,
                                  'track_artist': self.audio_info.track_artist,
                                  'track_duration': self.audio_info.track_duration,
                                  'act_duration': self.stage_info.act_duration
                              })
        self.bid_eval = BidEvaluation.objects.filter(
            bid_id=self.act_id,
            evaluator_id=self.reviewer.resourceitem_id).first()
        if self.bid_eval is None:
            self.bid_eval = BidEvaluation(evaluator=self.reviewer, bid=self.act)
        if validate_perms(request, ('Act Coordinator',), require=False):
            self.actionform, self.actionURL = _create_action_form(self.act)
        else:
            self.actionform = False
            self.actionURL = False
        self.performer = PersonaForm(instance=self.act.performer,
                                     prefix='The Performer(s)')


    def bid_review_response(self, request):
        return render(request,
                      'gbe/bid_review.tmpl',
                      {'readonlyform': [self.actform, self.performer],
                       'reviewer': self.reviewer,
                       'form': self.form,
                       'actionform': self.actionform,
                       'actionURL': self.actionURL,
                       'conference': self.conference,
                       'old_bid': self.old_bid,
                       })


    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.act.is_current:
            return HttpResponseRedirect(
                reverse('act_view', urlconf='gbe.urls', args=[self.act_id]))
        self.form = BidEvaluationForm(instance=self.bid_eval)
        return self.bid_review_response(request)

    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.act.is_current:
            return HttpResponseRedirect(
                reverse('act_view', urlconf='gbe.urls', args=[self.act_id]))
        self.form = BidEvaluationForm(request.POST, instance=self.bid_eval)
        if self.form.is_valid():
            evaluation = self.form.save(commit=False)
            evaluation.evaluator = self.reviewer
            evaluation.bid = self.act
            evaluation.save()
            return HttpResponseRedirect(reverse('act_review_list',
                                                urlconf='gbe.urls'))
        else:
            return self.bid_review_response(request)

def _create_action_form(act):
    actionform = BidStateChangeForm(instance=act)
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
