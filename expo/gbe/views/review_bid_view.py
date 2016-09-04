from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.models import (
    Class,
    BidEvaluation,
)
from gbe.forms import (
    BidEvaluationForm,
    BidStateChangeForm,
    PersonaForm,
    ClassBidForm,
    ParticipantForm,
)
from gbe.functions import (
    validate_perms,
    get_conf,
)


class ReviewBidView(View):
    bid_state_change_form = BidStateChangeForm
    bid_evaluation_type = BidEvaluation
    bid_evaluation_form_type = BidEvaluationForm

    def create_action_form(self, bid):
        self.actionform = self.bid_state_change_form(instance=bid)
        self.actionURL = reverse(self.changestate_view_name,
                                 urlconf='gbe.urls',
                                 args=[bid.id])

    def bid_review_response(self, request):
        return render(request,
                      'gbe/bid_review.tmpl',
                      {'readonlyform': self.readonlyform_pieces,
                       'reviewer': self.reviewer,
                       'form': self.form,
                       'actionform': self.actionform,
                       'actionURL': self.actionURL,
                       'conference': self.conference,
                       'old_bid': self.old_bid,
                       })

    def create_object_form(self, initial={}):
        self.object_form = self.bid_form_type(instance=self.object,
                                              prefix=self.bid_prefix,
                                              initial=initial)

    def post_response_for_form(self, request):
        import pdb; pdb.set_trace()
        if self.form.is_valid():
            evaluation = self.form.save(commit=False)
            evaluation.evaluator = self.reviewer
            evaluation.bid = self.object
            evaluation.save()
            return HttpResponseRedirect(reverse(self.review_list_view_name,
                                                urlconf='gbe.urls'))
        else:
            return self.bid_review_response(request)

    def object_not_current_redirect(self):
        if self.object.is_current:
            return None
        return HttpResponseRedirect(
            reverse(self.bid_view_name,
                    urlconf='gbe.urls',
                    args=[self.object.id]))

    def get_object(self, request, object_id):
        self.object = get_object_or_404(self.object_type,
                                        id=object_id)

    def groundwork(self, request, args, kwargs):
        object_id = kwargs['object_id']
        self.get_object(request, object_id)
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        if validate_perms(request,
                          self.coordinator_permissions,
                          require=False):
            self.create_action_form(self.object)
        else:
            self.actionform = False
            self.actionURL = False
        self.conference, self.old_bid = get_conf(self.object)
        import pdb; pdb.set_trace()
        self.bid_eval = self.bid_evaluation_type.objects.filter(
            bid_id=self.object.pk,
            evaluator_id=self.reviewer.resourceitem_id).first()
        if self.bid_eval is None:
            self.bid_eval = self.bid_evaluation_type(
                evaluator=self.reviewer, bid=self.object)

    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = self.bid_evaluation_form_type(instance=self.bid_eval)
        return (self.object_not_current_redirect() or
                self.bid_review_response(request))

    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = self.bid_evaluation_form_type(request.POST,
                                      instance=self.bid_eval)

        return (self.object_not_current_redirect() or
                self.post_response_for_form(request))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewBidView, self).dispatch(*args, **kwargs)
