from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from expo.gbe_logging import log_func
from gbe.models import Biddable
from gbe.forms import BidStateChangeForm
from gbe.functions import (
    send_bid_state_change_mail,
    validate_perms,
)

class BidChangeStateView(View):
    
    @log_func
    def bid_state_change(self, request):
        form = BidStateChangeForm(request.POST, instance=self.object)
        if form.is_valid():
            self.object = form.save()
        else:
            return render(
                request,
                'gbe/bid_review.tmpl',
                {'actionform': False,
                 'actionURL': False})
        return HttpResponseRedirect(
            reverse(self.redirectURL, urlconf='gbe.urls'))

    def get_object(self, request, object_id):
        self.object = get_object_or_404(self.object_type,
                                        id=object_id)

    def prep_bid(self, request, args, kwargs):
        object_id = kwargs['object_id']
        self.get_object(request, object_id)
        self.get_bidder()
        self.reviewer = validate_perms(request, self.coordinator_permissions)    

    def notify_bidder(self, request):
        if str(self.object.accepted) != request.POST['accepted']:
            send_bid_state_change_mail(
                str(self.object_type.__name__).lower(),
                self.bidder.contact_email,
                self.bidder.get_badge_name(),
                int(request.POST['accepted']))

    
    def groundwork(self, request, args, kwargs):
        self.prep_bid(request, args, kwargs)
        self.notify_bidder(request)

    @log_func
    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return self.bid_state_change(request)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BidChangeStateView, self).dispatch(*args, **kwargs)
