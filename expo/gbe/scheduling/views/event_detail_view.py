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

        eventitem_view = get_event_display_info(eventitem_id)

        template = 'gbe/scheduling/event_detail.tmpl'
        return render(request,
                      template,
                      {'eventitem': eventitem_view,
                       'show_tickets': True,
                       'tickets': eventitem_view['event'].get_tickets,
                       'user_id': request.user.id})

    def dispatch(self, *args, **kwargs):
        return super(EventDetailView, self).dispatch(*args, **kwargs)
