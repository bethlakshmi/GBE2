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


class ReviewClassView(View):
    reviewer_permissions = ('Class Reviewers',)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewClassView, self).dispatch(*args, **kwargs)


    def groundwork(self, request, args, kwargs):
        class_id = kwargs['class_id']
        self.object = get_object_or_404(Class,id=class_id)
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        if validate_perms(request, ('Class Coordinator',), require=False):
            self.actionform = BidStateChangeForm(instance=self.object)
            self.actionURL = reverse('class_changestate',
                                urlconf='gbe.urls',
                                args=[self.object.id])
        else:
                self.actionform = False
                self.actionURL = False
        try:
            self.bid_eval = BidEvaluation.objects.filter(
                bid_id=self.object.id,
                evaluator_id=self.reviewer.resourceitem_id)[0]
        except:
            self.bid_eval = BidEvaluation(evaluator=self.reviewer,
                                     bid=self.object)
        self.conference, self.old_bid = get_conf(self.object)
        self.classform = ClassBidForm(instance=self.object, prefix='The Class')
        self.teacher = PersonaForm(instance=self.object.teacher,
                                   prefix='The Teacher(s)')
        self.contact = ParticipantForm(
            instance=self.object.teacher.performer_profile,
            prefix='Teacher Contact Info',
            initial={
                'email': self.object.teacher.performer_profile.user_object.email,
                'first_name':
                    self.object.teacher.performer_profile.user_object.first_name,
                'last_name':
                    self.object.teacher.performer_profile.user_object.last_name})
        self.form = BidEvaluationForm(instance=self.bid_eval)


    def bid_review_response(self, request):
        return render(request,
                      'gbe/bid_review.tmpl',
                      {'readonlyform': [self.classform, self.teacher, self.contact],
                       'reviewer': self.reviewer,
                       'form': self.form,
                       'actionform': self.actionform,
                       'actionURL': self.actionURL,
                       'conference': self.conference,
                       'old_bid': self.old_bid,
                       })

    def process_form(self):
        evaluation = self.form.save(commit=False)
        evaluation.evaluator = self.reviewer
        evaluation.bid = self.object
        evaluation.save()


    def get(self, request, *args, **kwargs):
        '''
        Show a bid  which needs to be reviewed by the current user.
        To show: display all information about the bid, and a standard
        review form.
        '''
        self.groundwork(request, args, kwargs)
        if not self.object.is_current:
            return HttpResponseRedirect(
                reverse('class_view', urlconf='gbe.urls', args=[self.object.id]))

        return self.bid_review_response(request)


    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.object.is_current:
            return HttpResponseRedirect(
                reverse('class_view', urlconf='gbe.urls', args=[self.object.id]))

        if self.form.is_valid():
            self.process_form()
            return HttpResponseRedirect(reverse('class_review_list',
                                                urlconf='gbe.urls'))
        else:
            return self.bid_review_response(request)
