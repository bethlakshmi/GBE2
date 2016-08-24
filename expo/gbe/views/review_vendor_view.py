from gbe.models import Vendor
from gbe.forms import (
    BidEvaluationForm,
    VendorBidForm,
)
from gbe.views import ReviewBidView


class ReviewVendorView(ReviewBidView):
    reviewer_permissions = ('Vendor Reviewers',)
    coordinator_permissions = ('Vendor Coordinator')
    bid_prefix = 'The Vendor'
    bid_form_type = VendorBidForm
    object_type = Vendor
    review_list_view_name = 'vendor_review_list'
    bid_view_name = 'vendor_view'
    changestate_view_name = 'vendor_changestate'

    def groundwork(self, request, args, kwargs):
        super(ReviewVendorView, self).groundwork(request, args, kwargs)
        self.object_form = self.bid_form_type(instance=self.object,
                                              prefix=self.bid_prefix)
        self.readonlyform_pieces = [self.object_form]

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
