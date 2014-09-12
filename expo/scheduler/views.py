from django.shortcuts import render

# Create your views here.


def class_schedule(request):
    '''
    Schedule a class.
    '''

    pass

def event_schedule(request):
    '''
    Schedule an event.
    '''

    pass

def panel_schedule(request):
    '''
    Schedule a panel.
    '''

    pass

def calendar(request, cal_format = 'Block'):
    '''
    Top level calendar object.  Overall calendar for a site, sets some options,
    then calls calendar_view.
    '''

    pass

def calendar_view(request, cal_type = 'Event', cal_format = 'Block'):
    '''
    Accepts a calendar type, and renders a calendar for that type.  Type can be
    an event class, an event instance (shows what is scheduled within that
    event), an event reference (shows a calendar of just every instance of
    that event), or a schedulable items (which shows a calendar for that item).
    '''

    pass

