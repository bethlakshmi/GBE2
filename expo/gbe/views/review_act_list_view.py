from django.core.urlresolvers import reverse
from gbe.models import (
    Act,
    ActBidEvaluation,
    EvaluationCategory,
)
from review_bid_list_view import ReviewBidListView
from django.db.models import Avg


class ReviewActListView(ReviewBidListView):
    reviewer_permissions = ('Act Reviewers', )
    object_type = Act
    bid_evaluation_type = ActBidEvaluation
    template = 'gbe/act_bid_review_list.tmpl'
    bid_review_view_name = 'act_review'
    bid_review_list_view_name = 'act_review_list'
    bid_order_fields = ('accepted', 'performer')

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'categories': EvaluationCategory.objects.filter(visible=True),
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}

    def get_rows(self, bids, review_query):
        rows = []
        categories = EvaluationCategory.objects.filter(
            visible=True).order_by('category')
        for bid in bids:
            bid_row = {}
            bid_row['bidder_active'] = bid.bidder_is_active
            bid_row['bid'] = bid.bid_review_summary
            bid_row['reviews'] = []
            for category in categories:
                average = categories.filter(
                    category=category,
                    flexibleevaluation__bid=bid,
                    flexibleevaluation__ranking__gt=-1).aggregate(Avg(
                    'flexibleevaluation__ranking')),
                if average[0]['flexibleevaluation__ranking__avg']:
                    bid_row['reviews'] += [int(round(
                        average[0]['flexibleevaluation__ranking__avg']))]
                else:
                    bid_row['reviews'] += ["--"]
            bid_row['id'] = bid.id
            bid_row['review_url'] = reverse(self.bid_review_view_name,
                                            urlconf='gbe.urls',
                                            args=[bid.id])
            self.row_hook(bid, bid_row)
            rows.append(bid_row)
        return rows