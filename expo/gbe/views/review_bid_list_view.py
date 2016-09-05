from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render

from expo.gbe_logging import log_func
from gbe.functions import validate_perms
from gbe.models import (
    Act,
    BidEvaluation,
    Conference,
)


class ReviewBidListView(View):
    bid_evaluation_type = BidEvaluation
    template = 'gbe/bid_review_list.tmpl'
    bid_order_fields =('accepted', 'title')


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewBidListView, self).dispatch(*args, **kwargs)


    def get_bids(self):
        return self.object_type.objects.filter(
            submitted=True,
            conference=self.conference).order_by(*self.bid_order_fields)

    def review_query(self, bids):
        return self.bid_evaluation_type.objects.filter(
            bid=bids).select_related(
                'evaluator'
            ).order_by('bid', 'evaluator')

    def row_hook(self, bid, row):
        # override on subclass
        pass


    def get_rows(self, bids, review_query):
        rows = []
        for bid in bids:
            bid_row = {}
            bid_row['bid'] = bid.bid_review_summary
            bid_row['reviews'] = review_query.filter(
                bid=bid.id).select_related(
                    'evaluator').order_by(
                        'evaluator')
            bid_row['id'] = bid.id
            bid_row['review_url'] = reverse(self.bid_review_view_name,
                                            urlconf='gbe.urls',
                                            args=[bid.id])
            self.row_hook(bid, bid_row)
            rows.append(bid_row)
        return rows

    def get_bid_list(self):
        bids = self.get_bids()
        review_query = self.review_query(bids)
        self.rows = self.get_rows(bids, review_query)


    def get(self, request, *args, **kwargs):
        reviewer = validate_perms(request, self.reviewer_permissions)
        self.user = request.user
        if request.GET.get('conf_slug'):
            self.conference = Conference.by_slug(request.GET['conf_slug'])
        else:
            self.conference = Conference.current_conf()

        try:
            self.get_bid_list()
        except IndexError:
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

        self.conference_slugs = Conference.all_slugs()
        return render(request, self.template,
                      self.get_context_dict())
