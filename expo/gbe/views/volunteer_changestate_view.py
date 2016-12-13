from django.contrib.auth.decorators import login_required
from expo.gbe_logging import log_func
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from gbe.functions import validate_perms
from gbe.models import Volunteer

from gbe.forms import VolunteerBidStateChangeForm


@login_required
@log_func
def VolunteerChangeStateView(request, bid_id):
    '''
    Fairly specific to volunteer - removes the profile from all volunteer
    commitments, and resets the volunteer to the selected volunteer
    positions (if accepted), and then does the regular state change
    NOTE: only call on a post request
    '''
    reviewer = validate_perms(request, ('Volunteer Coordinator',))

    if request.method == 'POST':
        volunteer = get_object_or_404(Volunteer, id=bid_id)
        form = VolunteerBidStateChangeForm(request.POST,
                                           request=request,
                                           instance=volunteer)
        if form.is_valid():
            form.save()
            volunteer.profile.notify_volunteer_schedule_change()
            return HttpResponseRedirect(reverse('volunteer_review_list',
                                                urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid_review.tmpl',
                          {'actionform': False,
                           'actionURL': False})
    return HttpResponseRedirect(reverse('volunteer_review_list',
                                        urlconf='gbe.urls'))
