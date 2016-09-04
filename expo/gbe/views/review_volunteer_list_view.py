from django.core.urlresolvers import reverse
from gbe.models import Volunteer
from gbe.functions import validate_perms
from review_bid_list_view import ReviewBidListView


class ReviewVolunteerListView(ReviewBidListView):
    reviewer_permissions = ('Volunteer Reviewers', )
    coordinator_permissions = ('Volunteer Coordinator', )

    object_type = Volunteer
    bid_review_view_name ='volunteer_review'
    bid_review_list_view_name = 'volunteer_review_list'
    bid_edit_view_name = 'volunteer_edit'
    bid_assign_view_name = 'volunteer_assign'


    def _show_edit(self, volunteer):
        return (validate_perms(self.request,
                               self.coordinator_permissions,
                               require=False) and
                volunteer.is_current)

    def get_bid_list(self):
        bids = self.object_type.objects.filter(
            submitted=True).filter(
                conference=self.conference).order_by('accepted')
        review_query = self.bid_evaluation_type.objects.filter(
            bid=bids).select_related(
            'evaluator'
        ).order_by('bid', 'evaluator')

        _rows = []
        for bid in bids:
            bid_row = {}
            bid_row['bid'] = bid.bid_review_summary
            bid_row['reviews'] = review_query.filter(
                bid=bid.id
            ).select_related(
                'evaluator'
            ).order_by('evaluator')

            bid_row['id'] = bid.id
            bid_row['review_url'] = reverse(self.bid_review_view_name,
                                            urlconf='gbe.urls',
                                            args=[bid.id])
            if self._show_edit(bid):
                bid_row['edit_url'] = reverse(self.bid_edit_view_name,
                                              urlconf='gbe.urls',
                                              args=[bid.id])
                bid_row['assign_url'] = reverse(self.bid_assign_view_name,
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
