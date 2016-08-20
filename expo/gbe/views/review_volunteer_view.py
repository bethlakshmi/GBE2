from django.views.generic import View
from django.utils.decorators import method_decorator
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
    Volunteer,
)
from gbe.forms import (
    BidEvaluationForm,
    BidStateChangeForm,
)
from gbe.views.volunteer_display_functions import get_volunteer_forms


class ReviewVolunteerView(View):
    reviewer_permissions = ('Volunteer Reviewers',)
    coordinator_permissions = ('Volunteer Coordinator',)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewVolunteerView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        object_id = kwargs.get('object_id', 0)
        if int(object_id) == 0:
            object_id = int(request.POST['volunteer'])

        self.reviewer = validate_perms(request, self.reviewer_permissions)
        self.object = get_object_or_404(
            Volunteer,
            id=object_id,
        )
        self.display_forms = get_volunteer_forms(self.object)
        self.conference, self.old_bid = get_conf(self.object)
        if validate_perms(request, self.coordinator_permissions, require=False):
            self.actionform = BidStateChangeForm(instance=self.object)
            self.actionURL = reverse('volunteer_changestate',
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



    def bid_review_response(self, request, form):
        return render(request,
                      'gbe/bid_review.tmpl',
                      {'readonlyform': self.display_forms,
                       'reviewer': self.reviewer,
                       'form': form,
                       'actionform': self.actionform,
                       'actionURL': self.actionURL,
                       'conference': self.conference,
                       'old_bid': self.old_bid,
                       })



    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.object.is_current:
            return HttpResponseRedirect(
                reverse('volunteer_view',
                        urlconf='gbe.urls',
                        args=[self.object.id]))

        # show info and inputs for review
        form = BidEvaluationForm(instance=self.bid_eval)
        return self.bid_review_response(request, form)

    def post(self, request, *args, **kwargs):

        self.groundwork(request, args, kwargs)
        if not self.object.is_current:
            return HttpResponseRedirect(
                reverse('volunteer_view',
                        urlconf='gbe.urls',
                        args=[self.object.id]))

        form = BidEvaluationForm(request.POST,
                                 instance=self.bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = self.reviewer
            evaluation.bid = self.object
            evaluation.save()
            return HttpResponseRedirect(reverse('volunteer_review_list',
                                                urlconf='gbe.urls'))
        else:
            return self.bid_review_response(request, form)
