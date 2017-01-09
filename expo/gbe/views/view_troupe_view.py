from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from expo.gbe_logging import log_func
from gbe.forms import (
    ParticipantForm,
    TroupeForm,
)
from gbe.functions import validate_profile
from gbe.models import Troupe
from gbe.views.functions import (
    get_participant_form,
    get_performer_form,
)


@login_required
@log_func
def ViewTroupeView(request, troupe_id=None):
    '''
    Show troupes to troupe members, only contact should edit.
    '''
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('troupe_create',
                                            urlconf='gbe.urls'))

    troupe = get_object_or_404(Troupe, resourceitem_id=troupe_id)
    form = get_performer_form(troupe, perf_type='Troupe')
    owner = get_participant_form(
            profile,
            prefix='Troupe Contact')
    return render(request,
                  'gbe/bid_view.tmpl',
                  {'readonlyform': [form, owner]})
