from expo.gbe_logging import log_func
from gbe.views import BidChangeStateView
from gbe.functions import validate_perms
from gbe.models import Class


class ClassChangeStateView(BidChangeStateView):
    object_type = Class
    coordinator_permissions = ('Class Coordinator', )
    redirectURL = 'class_review_list'

    def get_bidder(self):
        self.bidder = self.object.teacher.contact

    @log_func
    def bid_state_change(self, request):
        # if the class has been rejected/no decision, clear any schedule items.
        if request.POST['accepted'] not in ('2', '3'):
            self.object.scheduler_events.all().delete()
        return super(ClassChangeStateView, self).bid_state_change(
            request)
