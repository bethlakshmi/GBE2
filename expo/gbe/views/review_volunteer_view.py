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
    reviewer_permissions = ('Class Reviewers',)
    coordinator_permissions = ('Class Coordinator',)
    bid_prefix = "The Class"
    bidder_prefix = "The Teacher(s)"


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewVolunteerView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        self.volunteer_id = kwargs['volunteer_id']



    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        reviewer = validate_perms(request, ('Volunteer Reviewers',))
        if request.GET and request.GET.get('conf_slug'):
            conference = Conference.by_slug(request.GET['conf_slug'])
        else:
            conference = Conference.current_conf()

        if int(self.volunteer_id) == 0 and request.method == 'POST':
            self.volunteer_id = int(request.POST['volunteer'])
        volunteer = get_object_or_404(
            Volunteer,
            id=self.volunteer_id,
        )
        if not volunteer.is_current:
            return HttpResponseRedirect(
                reverse('volunteer_view',
                        urlconf='gbe.urls',
                        args=[self.volunteer_id]))
        conference, old_bid = get_conf(volunteer)

        display_forms = get_volunteer_forms(volunteer)

        if 'Volunteer Coordinator' in request.user.profile.privilege_groups:
            actionform = BidStateChangeForm(instance=volunteer)
            actionURL = reverse('volunteer_changestate',
                                urlconf='gbe.urls',
                                args=[self.volunteer_id])
        else:
            actionform = False
            actionURL = False
        '''
        if user has previously reviewed the bid, provide his review for update
        '''
        try:
            bid_eval = BidEvaluation.objects.filter(
                bid_id=self.volunteer_id,
                evaluator_id=reviewer.resourceitem_id)[0]
        except:
            bid_eval = BidEvaluation(evaluator=reviewer, bid=volunteer)
        # show info and inputs for review
        if request.method == 'POST':
            form = BidEvaluationForm(request.POST,
                                     instance=bid_eval)
            if form.is_valid():
                evaluation = form.save(commit=False)
                evaluation.evaluator = reviewer
                evaluation.bid = volunteer
                evaluation.save()
                return HttpResponseRedirect(reverse('volunteer_review_list',
                                                    urlconf='gbe.urls'))
            else:
                return render(request, 'gbe/bid_review.tmpl',
                              {'readonlyform': display_forms,
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
                          {'readonlyform': display_forms,
                           'reviewer': reviewer,
                           'form': form,
                           'actionform': actionform,
                           'actionURL': actionURL,
                           'conference': conference,
                           'old_bid': old_bid,
                           })


    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        reviewer = validate_perms(request, ('Volunteer Reviewers',))
        if request.GET and request.GET.get('conf_slug'):
            conference = Conference.by_slug(request.GET['conf_slug'])
        else:
            conference = Conference.current_conf()

        if int(self.volunteer_id) == 0 and request.method == 'POST':
            self.volunteer_id = int(request.POST['volunteer'])
        volunteer = get_object_or_404(
            Volunteer,
            id=self.volunteer_id,
        )
        if not volunteer.is_current:
            return HttpResponseRedirect(
                reverse('volunteer_view',
                        urlconf='gbe.urls',
                        args=[self.volunteer_id]))
        conference, old_bid = get_conf(volunteer)

        display_forms = get_volunteer_forms(volunteer)

        if 'Volunteer Coordinator' in request.user.profile.privilege_groups:
            actionform = BidStateChangeForm(instance=volunteer)
            actionURL = reverse('volunteer_changestate',
                                urlconf='gbe.urls',
                                args=[self.volunteer_id])
        else:
            actionform = False
            actionURL = False
        '''
        if user has previously reviewed the bid, provide his review for update
        '''
        try:
            bid_eval = BidEvaluation.objects.filter(
                bid_id=self.volunteer_id,
                evaluator_id=reviewer.resourceitem_id)[0]
        except:
            bid_eval = BidEvaluation(evaluator=reviewer, bid=volunteer)
        # show info and inputs for review
        if request.method == 'POST':
            form = BidEvaluationForm(request.POST,
                                     instance=bid_eval)
            if form.is_valid():
                evaluation = form.save(commit=False)
                evaluation.evaluator = reviewer
                evaluation.bid = volunteer
                evaluation.save()
                return HttpResponseRedirect(reverse('volunteer_review_list',
                                                    urlconf='gbe.urls'))
            else:
                return render(request, 'gbe/bid_review.tmpl',
                              {'readonlyform': display_forms,
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
                          {'readonlyform': display_forms,
                           'reviewer': reviewer,
                           'form': form,
                           'actionform': actionform,
                           'actionURL': actionURL,
                           'conference': conference,
                           'old_bid': old_bid,
                           })
