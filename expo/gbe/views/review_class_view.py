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
from gbe.views import ReviewBidView

class ReviewClassView(ReviewBidView):
    reviewer_permissions = ('Class Reviewers',)
    coordinator_permissions = ('Class Coordinator',)
    bid_prefix = "The Class"
    bidder_prefix = "The Teacher(s)"
    bidder_form_type = PersonaForm
    bid_form_type = ClassBidForm
    object_type = Class
    bid_view_name = 'class_view'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewClassView, self).dispatch(*args, **kwargs)


    def groundwork(self, request, args, kwargs):
        super(ReviewClassView, self).groundwork(request, args, kwargs)
        self.create_object_form()
        self.teacher = self.bidder_form_type(instance=self.object.teacher,
                                             prefix=self.bidder_prefix)
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
        self.readonlyform_pieces = [self.object_form, self.teacher, self.contact]


    def get(self, request, *args, **kwargs):
        '''
        Show a bid  which needs to be reviewed by the current user.
        To show: display all information about the bid, and a standard
        review form.
        '''
        self.groundwork(request, args, kwargs)
        return (self.object_not_current_redirect() or
                self.bid_review_response(request))


    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return (self.object_not_current_redirect() or
                self.post_response_for_form(request))
