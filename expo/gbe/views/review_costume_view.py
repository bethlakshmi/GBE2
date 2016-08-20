from django.views.generic import View
from django.utils.decorators import method_decorator
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


class ReviewCostumeView(View):
    reviewer_permissions =  ('Costume Reviewers', )
    coordinator_permissions = ('Costume Coordinator',)
    performer_prefix = "The Performer"
    bidder_prefix = "The Owner"
    bid_prefix = "The Costume"
    bidder_form_type = PersonaForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewCostumeView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        self.costume_id = kwargs.get('costume_id', 0)
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        self.costume = get_object_or_404(
            Costume,
            id=self.costume_id
        )
        self.conference, self.old_bid = get_conf(self.costume)
        self.costume_form = CostumeBidSubmitForm(instance=self.costume,
                                                 prefix=self.bid_prefix)
        self.details = CostumeDetailsSubmitForm(instance=self.costume)
        self.performer = self.bidder_form_type(instance=self.costume.performer,
                                     prefix=self.performer_prefix)
        if validate_perms(request, self.coordinator_permissions, require=False):
            self.actionform = BidStateChangeForm(instance=self.costume)
            self.actionURL = reverse('costume_changestate',
                                urlconf='gbe.urls',
                                args=[self.costume_id])
        else:
                self.actionform = False
                self.actionURL = False

        self.profile = ParticipantForm(
            instance=self.costume.profile,
            prefix=self.bidder_prefix,
            initial={
                'email': self.costume.profile.user_object.email,
                'first_name': self.costume.profile.user_object.first_name,
                'last_name': self.costume.profile.user_object.last_name})


        self.bid_eval = BidEvaluation.objects.filter(
                bid_id=self.costume_id,
                evaluator_id=self.reviewer.resourceitem_id).first()
        if self.bid_eval is None:
            bid_eval = BidEvaluation(evaluator=self.reviewer, bid=self.costume)
        self.form = BidEvaluationForm(instance=self.bid_eval)

    def bid_review_response(self, request):
        return render(request, 'gbe/bid_review.tmpl',
                      {'readonlyform': [
                          self.costume_form,
                          self.details,
                          self.performer,
                          self.profile],
                       'reviewer': self.reviewer,
                       'form': self.form,
                       'actionform': self.actionform,
                       'actionURL': self.actionURL,
                       'conference': self.conference,
                       'old_bid': self.old_bid,
                      })


    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.costume.is_current:
            return HttpResponseRedirect(
                reverse('costume_view', urlconf='gbe.urls', args=[self.costume_id]))

        return self.bid_review_response(request)


    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.costume.is_current:
            return HttpResponseRedirect(
                reverse('costume_view', urlconf='gbe.urls', args=[self.costume_id]))

        if self.form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = self.reviewer
            evaluation.bid = self.costume
            evaluation.save()
            return HttpResponseRedirect(reverse('costume_review_list',
                                                urlconf='gbe.urls'))
        else:
            return self.bid_review_response(request)
