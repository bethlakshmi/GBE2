from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from expo.gbe_logging import log_func
from gbe.functions import (
    get_conf,
    validate_perms,
)
from gbe.models import Volunteer
from scheduler.functions import get_events_and_windows


@login_required
@log_func
def AssignVolunteerView(request, volunteer_id):
    '''
    Show a bid  which needs to be assigned to shifts by the coordinator.
    To show: display useful information about the bid,
    If user is not a coordinator, politely decline to show anything.
    '''
    reviewer = validate_perms(request, ('Volunteer Coordinator',))

    if int(volunteer_id) == 0 and request.method == 'POST':
        volunteer_id = int(request.POST['volunteer'])
    volunteer = get_object_or_404(
        Volunteer,
        id=volunteer_id,
    )
    if not volunteer.is_current:
        return HttpResponseRedirect(reverse(
            'volunteer_view', urlconf='gbe.urls'))
    conference, old_bid = get_conf(volunteer)

    actionURL = reverse('volunteer_changestate',
                        urlconf='gbe.urls',
                        args=[volunteer_id])

    return render(request,
                  'gbe/assign_volunteer.tmpl',
                  {'volunteer': volunteer,
                   'bookings': volunteer.profile.get_bookings('Volunteer'),
                   'volunteer_event_windows': get_events_and_windows(
                    conference),
                   'actionURL': actionURL,
                   'conference': conference,
                   'old_bid': old_bid})
