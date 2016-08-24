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
from gbe.views import BidChangeStateView
from scheduler.models import Worker, Event
from django.contrib import messages


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
        
        # Clear all commitments
        Worker.objects.filter(
            _item=volunteer.profile,
            role='Volunteer').delete()

        # if the volunteer has been accepted, set the events.
        if request.POST['accepted'] == '3':
            for assigned_event in request.POST.getlist('events'):
                event = get_object_or_404(Event, pk=assigned_event)
                warnings = event.allocate_worker(
                        volunteer.profile,
                        'Volunteer')
                for warning in warnings:
                    messages.warning(request,
                                     warning)
        volunteer.profile.notify_volunteer_schedule_change()
    return BidChangeStateView(request, bid_id, 'volunteer_review_list')
