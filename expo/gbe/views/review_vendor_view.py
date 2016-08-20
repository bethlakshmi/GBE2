from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)

from expo.gbe_logging import log_func
from gbe.models import (
    BidEvaluation,
    Vendor,
)
from gbe.forms import (
    BidEvaluationForm,
    BidStateChangeForm,
    VendorBidForm,
)
from gbe.functions import (
    get_conf,
    validate_perms,
)

class ReviewVendorView(View):
    reviewer_permissions = ('Vendor Reviewers',)
    coordinator_permissions = ('Vendor Coordinator')
    bid_prefix = 'The Vendor'
    bid_form_type = VendorBidForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewVendorView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        object_id = kwargs['object_id']
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        self.object = get_object_or_404(
            Vendor,
            id=object_id,
        )
        self.conference, self.old_bid = get_conf(self.object)
        self.volform = self.bid_form_type(instance=self.object, prefix=self.bid_prefix )
        if validate_perms(request, self.coordinator_permissions, require=False):
            self.actionform = BidStateChangeForm(instance=self.object)
            self.actionURL = reverse('vendor_changestate',
                                urlconf='gbe.urls',
                                args=[object_id])
        else:
                self.actionform = False
                self.actionURL = False

        self.bid_eval = BidEvaluation.objects.filter(
            bid_id=object_id,
            evaluator_id=self.reviewer.resourceitem_id).first()
        if self.bid_eval is None:
            self.bid_eval = BidEvaluation(evaluator=self.reviewer, bid=self.object)


    def bid_review_response(self, request):
        return render(request,
                      'gbe/bid_review.tmpl',
                      {'readonlyform': [self.volform],
                       'reviewer': self.reviewer,
                       'form': self.form,
                       'actionform': self.actionform,
                       'actionURL': self.actionURL,
                       'conference': self.conference,
                       'old_bid': self.old_bid,
                       })

    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)

        if not self.object.is_current:
            return HttpResponseRedirect(
                reverse('vendor_view', urlconf='gbe.urls', args=[self.object.id]))

        # show act info and inputs for review
        self.form = BidEvaluationForm(instance=self.bid_eval)
        return self.bid_review_response(request)

    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.object.is_current:
            return HttpResponseRedirect(
                reverse('vendor_view', urlconf='gbe.urls', args=[self.object.id]))
        self.form = BidEvaluationForm(request.POST, instance=self.bid_eval)

        if self.form.is_valid():
            evaluation = self.form.save(commit=False)
            evaluation.evaluator = self.reviewer
            evaluation.bid = self.object
            evaluation.save()
            return HttpResponseRedirect(reverse('vendor_review_list',
                                                urlconf='gbe.urls'))
        else:
            return self.bid_review_response(request)
