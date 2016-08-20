from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe.forms import (
    BidEvaluationForm,
    PersonaForm,
    ClassBidForm,
    ParticipantForm,
)
from gbe.models import Class
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
        initial = {
            'email': self.object.teacher.performer_profile.user_object.email,
            'first_name':
            self.object.teacher.performer_profile.user_object.first_name,
            'last_name':
            self.object.teacher.performer_profile.user_object.last_name}
        self.contact = ParticipantForm(
            instance=self.object.teacher.performer_profile,
            prefix='Teacher Contact Info', initial=initial)
        self.form = BidEvaluationForm(instance=self.bid_eval)
        self.readonlyform_pieces = (self.object_form,
                                    self.teacher, self.contact)

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
