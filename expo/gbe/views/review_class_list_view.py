from django.core.urlresolvers import reverse
from gbe.models import Class

from review_bid_list_view import ReviewBidListView

class ReviewClassListView(ReviewBidListView):
    reviewer_permissions = ('Class Reviewers', )
    object_type = Class
    bid_review_view_name = 'class_review'
    bid_review_list_view_name = 'class_review_list'

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
