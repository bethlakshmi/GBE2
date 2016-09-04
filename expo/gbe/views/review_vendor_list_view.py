from django.core.urlresolvers import reverse
from gbe.models import Vendor
from review_bid_list_view import ReviewBidListView

class ReviewVendorListView(ReviewBidListView):
    reviewer_permissions = ('Vendor Reviewers',)
    object_type = Vendor
    bid_review_view_name = 'vendor_review'
    bid_review_list_view_name = 'vendor_review_list'

    def get_bid_list(self):
        bids = self.get_bids()
        review_query = self.review_query(bids)
        self.rows = self.get_rows(bids, review_query)

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'rows': self.rows,
                'action1_text': 'Review',
                'action1_link': reverse(self.bid_review_list_view_name,
                                        urlconf='gbe.urls'),
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
