from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe.forms import (
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
    ParticipantForm,
    PersonaForm,
    BidEvaluationForm,
)
from gbe.models import Costume
from gbe.views import ReviewBidView


class ReviewCostumeView(ReviewBidView):
    reviewer_permissions = ('Costume Reviewers',)
    coordinator_permissions = ('Costume Coordinator',)
    performer_prefix = "The Performer"
    bidder_prefix = "The Owner"
    bid_prefix = "The Costume"
    bidder_form_type = PersonaForm
    object_type = Costume
    bid_form_type = CostumeBidSubmitForm
    bid_view_name = "costume_view"
    review_list_view_name = 'costume_review_list'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewCostumeView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        super(ReviewCostumeView, self).groundwork(request, args, kwargs)
        self.details = CostumeDetailsSubmitForm(instance=self.object)
        self.performer = self.bidder_form_type(instance=self.object.performer,
                                               prefix=self.performer_prefix)
        self.create_object_form()

        self.profile = ParticipantForm(
            instance=self.object.profile,
            prefix=self.bidder_prefix,
            initial={
                'email': self.object.profile.user_object.email,
                'first_name': self.object.profile.user_object.first_name,
                'last_name': self.object.profile.user_object.last_name})

        self.readonlyform_pieces = [
            self.object_form,
            self.details,
            self.performer,
            self.profile]

    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = BidEvaluationForm(instance=self.bid_eval)
        return (self.object_not_current_redirect() or
                self.bid_review_response(request))

    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = BidEvaluationForm(request.POST, instance=self.bid_eval)
        return (self.object_not_current_redirect() or
                self.post_response_for_form(request))
