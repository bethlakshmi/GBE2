from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    get_object_or_404,
)
from expo.gbe_logging import log_func
from gbe.models import Volunteer
from gbe.functions import validate_perms
from gbe.views.volunteer_display_functions import get_volunteer_forms


@login_required
@log_func
def ViewVolunteerView(request, volunteer_id):
    '''
    Show a bid  which needs to be reviewed by the current user.
    To show: display all information about the bid, and a standard
    review form.
    If user is not a reviewer, politely decline to show anything.
    '''
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    if volunteer.profile != request.user.profile:
        validate_perms(request, ('Volunteer Reviewers',), require=True)

    display_forms = get_volunteer_forms(volunteer)

    return render(request, 'gbe/bid_view.tmpl',
                  {'readonlyform': display_forms})
