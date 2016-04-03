from django.contrib.auth.decorators import login_required
from expo.gbe_logging import log_func
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    render,
    get_object_or_404,
    render_to_response,
)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    Http404,
)
from django.template import (
    loader,
    RequestContext,
    Context,
)
from gbe.models import (
    Event,
    Act,
    Performer,
    Conference,
)
from gbe.forms import *

from gbe.functions import *

from gbe.ticketing_idd_interface import (
    verify_performer_app_paid,
    verify_vendor_app_paid,
    get_purchased_tickets,
    vendor_submittal_link,
    performer_act_submittal_link,
)
from scheduler.functions import (
    set_time_format,
    get_events_and_windows
)
from scheduler.models import (
    Event as sEvent,
    ResourceAllocation,
    Worker,
)

visible_bid_query = (Q(biddable_ptr__conference__status='upcoming') |
                     Q(biddable_ptr__conference__status='ongoing'))


class_durations = {0: 0, 1: 60, 2: 90, 3: 120}
