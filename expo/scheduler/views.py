from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from scheduler.models import *
from scheduler.forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.forms.models import inlineformset_factory
import gbe_forms_text
from django.core.urlresolvers import reverse


# Create your views here.

def selfcast(sobj):
    '''
    Takes a scheduler object and casts it to its underlying type. 
    This can (will) fail if object ids are out of sync, see issue 145 
    Pretty rudimentary, can probably be improved
    '''
    try:
        return sobj.typeof.objects.get(id=sobj.id)
    except:
        return sobj


def get_events_display_info():
    '''
    Helper for displaying lists of events. Gets a supply of conference event items and munges 
    them into displayable shape
    "Conference event items" = things in the conference model which extend EventItems and therefore 
    could be Events
    '''
    eventitems = EventItem.objects.select_subclasses()
    eventitems = [{'eventitem': item, 
                   'confitem':selfcast(item), 
                   'scheduled_events':item.scheduler_events.all()}
                  for item in eventitems]
    eventslist = [ {'title' : entry['confitem'].sched_payload['title'],
                    'locations': [event.location for event in entry['scheduled_events']],
                    'datetime': [event.start_time for event in entry['scheduled_events']],
                    'duration': entry['confitem'].sched_payload['duration'],
                    'type':entry['confitem'].sched_payload['type']
                    }
                   for entry in eventitems]
    return eventslist

def get_event_display_info(eventitem_id):
    '''
    Helper for displaying a single of event. Same idea as get_events_display_info - but for
    only one eventitem.  
    '''
    item = EventItem.objects.get_subclass(event=eventitem_id)
    eventitem_view = {'event': item, 
                      'scheduled_events':item.scheduler_events.all()}

    return eventitem_view

def class_schedule(request):
    '''
    Schedule a class.
    '''

    pass

def event_schedule(request):
    '''
    Schedule a event.
    '''

    pass

@login_required
def event_list(request):
    '''
    List of events (all)
    '''
    from gbe.models import Profile
    if request.user.is_authenticated():
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return render_to_response ('gbe/index_unregistered_user.tmpl')  # works?
    else:
        return render_to_response ('gbe/index')  # works?

    header  = [ 'Title','Location','Date/Time','Duration','Type',]
    events = get_events_display_info()

    form = EventsDisplayForm()
    template = 'scheduler/events_review_list.tmpl'
    return render(request, template, {'form' : form})




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

def detail_view(request, eventitem_id):
    '''
    Takes the id of a single event and displays all its details in a template
    '''
    eventitem_view = get_event_display_info(eventitem_id)
    template = 'scheduler/event_detail.tmpl'
    return render(request, template, {'eventitem': eventitem_view,
                                      'show_tickets': True,
                                      'tickets': eventitem_view['event'].get_tickets,
                                      'user_id':request.user.id})

