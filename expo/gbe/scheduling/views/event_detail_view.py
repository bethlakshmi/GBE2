from django.views.generic import View
from django.shortcuts import (
    render,
)
from gbe.scheduling.views.functions import (
    get_event_display_info,
)


class EventDetailView(View):
    '''
    Takes the id of a single event_item and displays all its
    details in a template
    '''
    
    def get(self, request, *args, **kwargs):
        eventitem_id = kwargs['eventitem_id']
        toggle = "on"
        eventitem_view = get_event_display_info(eventitem_id)
        if request.user.is_authenticated() and request.user.profile and \
                eventitem_view['event'].e_conference.status != "completed":
            for item in eventitem_view['scheduled_events']:
                for person in item.people:
                    if person.user == request.user and person.role == "Interested":
                        toggle = "off"
        
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
