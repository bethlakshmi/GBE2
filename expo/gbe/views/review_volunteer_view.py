from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe.models import Volunteer

from gbe.forms import BidEvaluationForm
from gbe.views import ReviewBidView
from gbe.views.volunteer_display_functions import get_volunteer_forms


class ReviewVolunteerView(ReviewBidView):
    reviewer_permissions = ('Volunteer Reviewers',)
    coordinator_permissions = ('Volunteer Coordinator',)
    object_type = Volunteer
    review_list_view_name = 'volunteer_review_list'
    bid_view_name = 'volunteer_view'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewVolunteerView, self).dispatch(*args, **kwargs)

    def get_object(self, request, object_id):
        if int(object_id) == 0:
            object_id = int(request.POST['volunteer'])
        super(ReviewVolunteerView, self).get_object(request, object_id)

    def groundwork(self, request, args, kwargs):
        super(ReviewVolunteerView, self).groundwork(request, args, kwargs)

        self.readonlyform_pieces = get_volunteer_forms(self.object)

    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = BidEvaluationForm(instance=self.bid_eval)
        return (self.object_not_current_redirect() or
                self.bid_review_response(request))

    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = BidEvaluationForm(request.POST,
                                      instance=self.bid_eval)

        return (self.object_not_current_redirect() or
                self.post_response_for_form(request))
