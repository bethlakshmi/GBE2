from django.core.urlresolvers import reverse

from gbe.models import (
    Act,
    BidEvaluation,
)
from review_bid_list_view import ReviewBidListView

class ReviewActListView(ReviewBidListView):
    reviewer_permissions = ('Act Reviewers', )
    object_type = Act
    bid_evaluation_type = BidEvaluation
    bid_review_view_name = 'act_review'
    bid_review_list_view_name = 'act_review_list'
    bid_order_fields = ('accepted', 'performer')

    def get_bid_list(self):
        bids = self.get_bids()
        review_query = self.review_query(bids)
        self.rows = self.get_rows(bids, review_query)

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
