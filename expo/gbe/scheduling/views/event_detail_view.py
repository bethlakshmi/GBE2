from django.views.generic import View
from django.shortcuts import (
    render,
)
from gbe.scheduling.views.functions import (
    get_event_display_info,
)
from scheduler.idd import get_schedule


class EventDetailView(View):
    '''
    Takes the id of a single event_item and displays all its
    details in a template
    '''
    def get(self, request, *args, **kwargs):
        eventitem_id = kwargs['eventitem_id']
        toggle = "on"
        eventitem_view = get_event_display_info(eventitem_id)
        if eventitem_view['event'].calendar_type == "Volunteer" or (
                eventitem_view['event'].e_conference.status == "completed"):
            toggle = None
        elif request.user.is_authenticated() and request.user.profile:
            sched_response = get_schedule(
                request.user,
                labels=[eventitem_view['event'].calendar_type,
                        eventitem_view['event'].e_conference.conference_slug])
            for booking in sched_response.schedule_items:
                if booking.event in eventitem_view['scheduled_events']:
                    if booking.role == "Interested":
                        toggle = "off"
                    else:
                        toggle = "disabled"
        template = 'gbe/scheduling/event_detail.tmpl'
        return render(request,
                      template,
                      {'eventitem': eventitem_view,
                       'show_tickets': True,
                       'tickets': eventitem_view['event'].get_tickets,
                       'user_id': request.user.id,
                       'toggle': toggle})

    def dispatch(self, *args, **kwargs):
        return super(EventDetailView, self).dispatch(*args, **kwargs)
