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
        conference, old_bid = get_conf(self.object)
        classform = ClassBidForm(instance=self.object, prefix='The Class')
        teacher = PersonaForm(instance=self.object.teacher,
                              prefix='The Teacher(s)')
        contact = ParticipantForm(
            instance=self.object.teacher.performer_profile,
            prefix='Teacher Contact Info',
            initial={
                'email': self.object.teacher.performer_profile.user_object.email,
                'first_name':
                    self.object.teacher.performer_profile.user_object.first_name,
                'last_name':
                    self.object.teacher.performer_profile.user_object.last_name})

        '''
        if user has previously reviewed the class, provide their review for update
        '''
        try:
            bid_eval = BidEvaluation.objects.filter(
                bid_id=self.object.id,
                evaluator_id=self.reviewer.resourceitem_id)[0]
        except:
            bid_eval = BidEvaluation(evaluator=self.reviewer,
                                     bid=self.object)

        form = BidEvaluationForm(instance=bid_eval)
        return render(request,
                      'gbe/bid_review.tmpl',
                      {'readonlyform': [classform, teacher, contact],
                       'reviewer': self.reviewer,
                       'form': form,
                       'actionform': self.actionform,
                       'actionURL': self.actionURL,
                       'conference': conference,
                       'old_bid': old_bid,
                       })


    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.object.is_current:
            return HttpResponseRedirect(
                reverse('class_view', urlconf='gbe.urls', args=[self.object.id]))
        conference, old_bid = get_conf(self.object)
        classform = ClassBidForm(instance=self.object, prefix='The Class')
        teacher = PersonaForm(instance=self.object.teacher,
                              prefix='The Teacher(s)')
        contact = ParticipantForm(
            instance=self.object.teacher.performer_profile,
            prefix='Teacher Contact Info',
            initial={
                'email': self.object.teacher.performer_profile.user_object.email,
                'first_name':
                    self.object.teacher.performer_profile.user_object.first_name,
                'last_name':
                    self.object.teacher.performer_profile.user_object.last_name})

        '''
        if user has previously reviewed the class, provide their review for update
        '''
        try:
            bid_eval = BidEvaluation.objects.filter(
                bid_id=self.object.id,
                evaluator_id=self.reviewer.resourceitem_id)[0]
        except:
            bid_eval = BidEvaluation(evaluator=self.reviewer,
                                     bid=self.object)

    # show class info and inputs for review

        form = BidEvaluationForm(request.POST,
                                 instance=bid_eval)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.evaluator = self.reviewer
            evaluation.bid = self.object
            evaluation.save()
            return HttpResponseRedirect(reverse('class_review_list',
                                                urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid_review.tmpl',
                          {'readonlyform': [classform, teacher, contact],
                           'reviewer': self.reviewer,
                           'form': form,
                           'actionform': self.actionform,
                           'actionURL': self.actionURL,
                           'conference': conference,
                           'old_bid': old_bid,
                           })
