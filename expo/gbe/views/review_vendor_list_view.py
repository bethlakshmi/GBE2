from django.core.urlresolvers import reverse
from gbe.models import Vendor
from review_bid_list_view import ReviewBidListView

class ReviewVendorListView(ReviewBidListView):
    reviewer_permissions = ('Vendor Reviewers',)
    object_type = Vendor
    bid_review_view_name = 'vendor_review'
    bid_review_list_view_name = 'vendor_review_list'

    def get_bid_list(self):
        bids = self.object_type.objects.filter(
            submitted=True).filter(
                conference=self.conference).order_by(
                    'accepted',
                    'title')
        review_query = self.bid_evaluation_type.objects.filter(
            bid=bids).select_related(
                'evaluator').order_by('bid',
                                      'evaluator')
        _rows = []
        for bid in bids:
            bid_row = {}
            bid_row['bid'] = bid.bid_review_summary
            bid_row['reviews'] = review_query.filter(
                bid=bid.id).select_related(
                    'evaluator').order_by('evaluator')
            bid_row['id'] = bid.id
            bid_row['review_url'] = reverse(self.bid_review_view_name,
                                            urlconf='gbe.urls',
                                            args=[bid.id])
            _rows.append(bid_row)
        self.rows = _rows


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
