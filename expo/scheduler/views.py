from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
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
from datetime import datetime
from datetime import time as dttime
from table import table
from gbe.duration import Duration
from scheduler.functions import tablePrep
from scheduler.functions import set_time_format


# Create your views here.


def validate_profile(request):
    '''
    Return the user profile if any
    '''
    from gbe.models import Profile
    if request.user.is_authenticated():
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            return False


def validate_perms(request, perms):
    '''
    Validate that the requesting user has the stated permissions
    Returns profile object if perms exist, False if not
    '''
    profile = validate_profile(request)
    if not profile:
        raise Http404
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    raise Http404

def selfcast(sobj):
    '''
    Takes a scheduler object and casts it to its underlying type. 
    This can (will) fail if object ids are out of sync, see issue 145 
    Pretty rudimentary, can probably be improved
    '''
    try:
        return sobj.typeof().objects.get(pk=sobj.child.id)
    except:
        return sobj


def get_events_display_info(time_format = None):
    '''
    Helper for displaying lists of events. Gets a supply of conference event items and munges 
    them into displayable shape
    "Conference event items" = things in the conference model which extend EventItems and therefore 
    could be Events
    '''

    if time_format == None: time_format = set_time_format(days = 2)
    eventitems = EventItem.objects.select_subclasses()
    eventitems = [item for item in eventitems] 
    eventitems = [{'eventitem': item, 
                   'confitem':selfcast(item), 
                   'schedule_event':item.scheduler_events.all().first()}
                  for item in eventitems]
    import gbe.models as gbe
    eventitems = [item for item in eventitems if isinstance(item['confitem'], gbe.Class) 
                  and item['confitem'].accepted ==3]
    eventslist = []
    for entry in eventitems:
        eventinfo = {'title' : entry['confitem'].sched_payload['title'],
                'duration': entry['confitem'].sched_payload['duration'],
                    'type':entry['confitem'].sched_payload['details']['type'],
                    'detail': reverse('detail_view', urlconf='scheduler.urls', 
                                      args = [entry['eventitem'].eventitem_id]),
                    'edit': reverse('edit_event', urlconf='scheduler.urls', 
                                    args =  [entry['eventitem'].eventitem_id]),
                    }
        if entry['schedule_event']:
            eventinfo ['location'] = entry['schedule_event'].location
            eventinfo ['datetime'] =  entry['schedule_event'].starttime.strftime(time_format)
            eventinfo ['max_volunteer'] =  entry['schedule_event'].max_volunteer
        else:
            eventinfo ['location'] = "Not yet scheduled"
            eventinfo ['datetime'] = "Not yet scheduled"
            eventinfo ['max_volunteer'] =  "N/A"
        eventslist.append(eventinfo)
    '''
    eventslist = [ {'title' : entry['confitem'].sched_payload['title'],
                    'location': entry['schedule_event'].location,
                    'datetime': entry['schedule_event'].starttime.strftime('%A, %I:%M %p'),
                    'duration': entry['confitem'].sched_payload['duration'],
                    'type':entry['confitem'].sched_payload['details']['type'],
                    'detail': reverse('detail_view', urlconf='scheduler.urls', 
                                      args = [entry['eventitem'].eventitem_id]),
                    'edit': reverse('edit_event', urlconf='scheduler.urls', 
                                    args =  [entry['eventitem'].eventitem_id]),
                    }
                   for entry in eventitems]

    '''
    return eventslist

def get_event_display_info(eventitem_id):
    '''
    Helper for displaying a single of event. Same idea as get_events_display_info - but for
    only one eventitem.  
    '''
    item = EventItem.objects.filter(eventitem_id=eventitem_id).select_subclasses()[0]
    
    bio_grid_list = []
    for sched_event in item.scheduler_events.all():
        bio_grid_list += sched_event.bio_list
    
    eventitem_view = {'event': item, 
                      'scheduled_events':item.scheduler_events.all(),
                      'labels': event_labels,
                      'bio_grid_list': bio_grid_list
                     }

    return eventitem_view

def class_schedule(request):
    '''
    Schedule a class.
    '''

    pass



def event_schedule(request, event_id):
    '''
    Schedule a event: create a scheduler.event object, set start time/day, and allocate a room
    '''
    


@login_required
def event_list(request):
    '''
    List of events (all)
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))
                                                             
    header  = [ 'Title','Location','Date/Time','Duration','Type','Max Volunteer','Detail', 'Edit Schedule']
    events = get_events_display_info()


    template = 'scheduler/events_review_list.tmpl'
    return render(request, template, { 'events':events, 'header':header})




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

#def calendar_view(request, cal_type = 'Event', cal_format = 'Block'):
#    '''
#    Accepts a calendar type, and renders a calendar for that type.  Type can be
#    an event class, an event instance (shows what is scheduled within that
#    event), an event reference (shows a calendar of just every instance of
#    that event), or a schedulable items (which shows a calendar for that item).
#    '''

#    pass

def detail_view(request, eventitem_id):
    '''
    Takes the id of a single event and displays all its details in a template
    '''
    eventitem_view = get_event_display_info(eventitem_id)
    template = 'scheduler/event_schedule.tmpl'
    return render(request, template, {'eventitem': eventitem_view,
                                      'show_tickets': True,
                                      'tickets': eventitem_view['event'].get_tickets,
                                      'user_id':request.user.id,
                                      })


def edit_event(request, eventitem_id):
    '''
    Add an item to the conference schedule and/or set its schedule details (start
    time, location, duration, or allocations)
    Takes a scheduler.EventItem id
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))

    try:
        item = EventItem.objects.get_subclass(eventitem_id = eventitem_id)
    except:
        raise Exception ("Error code XYZZY: Couldn't get an item for id")
    
    if request.method=='POST':
        if len(item.scheduler_events.all())==0:
               # Creating a new scheduler.Event and allocating a room
            event_form = EventScheduleForm(request.POST, 
                                     prefix='event')
        else:
            event_form = EventScheduleForm(request.POST, 
                                           instance = item.scheduler_events.all()[0],
                                           prefix='event')
        if (event_form.is_valid()  and True):
            s_event=event_form.save(commit=False)
            s_event.eventitem = item
            data = event_form.cleaned_data

                         
            if data['duration']:
                s_event.set_duration(data['duration'])
            l = [l for l in LocationItem.objects.select_subclasses() if str(l) == data['location']][0]
            s_event.save()                        
            s_event.set_location(l)
            s_event.save()                        
            
            return HttpResponseRedirect(reverse('event_schedule', urlconf='scheduler.urls'))
        else:
            return HttpResponseRedirect(reverse('error', urlconf='gbe.urls'))
    else:
        old_events = item.scheduler_events.all()
        duration = item.event.sched_payload['duration']
        if len(old_events) > 0:
            event = old_events[0]
            day = event.starttime.strftime("%A")
            time = event.starttime.strftime("%H:%M")
            location = event.location
            form = EventScheduleForm(prefix = "event", 
                                           initial = {'day':day, 
                                                      'time':time,
                                                      'location': location, 
                                                      'duration':duration})
        else: 
            form =  EventScheduleForm( prefix='event', initial={'duration':duration})
    template = 'scheduler/event_schedule.tmpl'
    eventitem_view = get_event_display_info(eventitem_id)
    return render(request, template, {'eventitem': eventitem_view,
                                      'form': form,
                                      'show_tickets': True,
                                      'tickets': eventitem_view['event'].get_tickets,
                                      'user_id':request.user.id})
def view_list(request, event_type='All'):
    '''
    One function to cut down on replicating code.  If adding a new view-only event list, do the following;
      - figure out whether it's a GenericEvent with a type (1st case statement) or a subclass
         NOTE: can't filter on a property.
      - add the type of list you want to have to the list_titles dictionary in gbetext
      - add the text for the list you want to have to the list_text dicionary
      - double check if any new label text needs to be added to event_labels
         LATER:  I'd like to find a way to get all this ugly large text blobs in *.py files and into the
         DB where Scratch can change them - Betty
    '''
    from gbe.models import Class, Show, GenericEvent

    try:
        items = []
        event_types = dict(event_options)
        class_types = dict(class_options)

        ''' BB - darn it, this is less open ended than I wanted but after finding that there is
        no elegant filter for child class type, and that select_subclasses isn't a *filter* - I gave up
        '''
        if event_types.has_key(event_type):
            items = GenericEvent.objects.filter(type=event_type)
        elif class_types.has_key(event_type):
            items = Class.objects.filter(accepted='3', type=event_type)
        elif event_type=='Show':
            items = Show.objects.all()
        elif event_type=='Class':
            items = Class.objects.filter(accepted='3')
        else:
            items = EventItem.objects.all().select_subclasses()
            event_type="All"

        events = [{'eventitem': item, 
                    'scheduled_events':item.scheduler_events.all(),
                    'detail': reverse('detail_view', urlconf='scheduler.urls', 
                                      args = [item.eventitem_id])}
                    for item in items]
    except:
        events = None
    return render(request, 'scheduler/event_display_list.tmpl',
                  {'title': list_titles[event_type],
                   'view_header_text': list_text[event_type],
                   'labels': event_labels,
                   'events': events})


def calendar_view(request, cal_type = 'Event', cal_times = (datetime(2015, 02, 20, 18, 00), datetime(2015, 02, 23, 00,00)), time_format=None, duration = Duration(minutes = 30)):
    '''
    A view to query the database for events of type cal_type over the period of time cal_times,
    and turn the information into a calendar in block format for display.

    Or it will be, eventually.  Right now it is using dummy event information for testing purposes.
    Will add in database queries once basic funcationality is completed.
    '''

    events = []
    events = calendar_test_data

    if time_format == None: 
        time_format = set_time_format()

    Table = {}
    Table['rows'] = tablePrep(events, duration)
    Table['Name'] = 'Event Calendar for the Great Burlesque Expo of 2015'
    Table['Link'] = 'http://burlesque-expo.com'
    Table['X_Name'] = {}
    Table['X_Name']['html'] = 'Rooms'
    Table['X_Name']['Link'] = 'http://burlesque-expo.com/class_rooms'   ## Fix This!!!

    template = 'scheduler/Sched_Display.tmpl'

    

    return render(request, template, Table)
    

calendar_test_data =     [{'html': 'Horizontal Pole Dancing 101', 'Link': 'http://some.websi.te', \
        'starttime': datetime(2015, 02, 07, 9, 00), 
        'stoptime': datetime(2015, 02, 07, 10, 00), \
        'location': 'Paul Revere', 'Type': 'Movement Class'}, 

    {'html': 'Shimmy Shimmy, Shake', 'Link': 'http://some.new.websi.te', \
        'starttime': datetime(2015, 02, 07, 13, 00), 
        'stoptime': datetime(2015, 02, 07, 14, 00), \
        'location': 'Paul Revere', 'Type': 'Movement Class'},

    {'html': 'Jumpsuit Removes', 'Link': 'http://some.other.websi.te', \
        'starttime': datetime(2015, 02, 07, 10, 00), 
        'stoptime': datetime(2015, 02, 07, 11, 00), \
        'location': 'Paul Revere', 'Type': 'Movement Class'},

    {'html': 'Tax Dodging for Performers', 'Link': 'http://yet.another.websi.te', \
        'starttime': datetime(2015, 02, 07, 11, 00), 
        'stoptime': datetime(2015, 02, 07, 12, 00), \
        'location': 'Paul Revere', 'Type': 'Business Class'},

    {'html': 'Butoh Burlesque', 'Link': 'http://japanese.websi.te', \
        'starttime': datetime(2015, 02, 07, 9, 00), 
        'stoptime': datetime(2015, 02, 07, 10, 00), \
        'location': 'Thomas Atkins', 'Type': 'Movement Class'},

    {'html': 'Kick Left, Kick Face, Kick Ass: Burly-Fu', \
        'Link': 'http://random.new.websi.te', \
        'starttime': datetime(2015, 02, 07, 14, 00), 
        'stoptime': datetime(2015, 02, 07, 16, 00),\
        'location': 'Thomas Atkins', 'Type': 'Movement Class'},

    {'html': 'Muumuus A-Go-Go', 'short_desc': 'Dancing in Less-then-Sexy Clothing', \
        'Link': 'http://some.bad.websi.te', \
        'starttime': datetime(2015, 02, 07, 10, 00), 
        'stoptime': datetime(2015, 02, 07, 12, 00), \
        'location': 'Thomas Atkins', 'Type': 'Movement Class'},

    {'html': 'From Legalese to English, Contracts in Burlesque', \
        'Link': 'http://still.another.websi.te', \
        'starttime': datetime(2015, 02, 07, 12, 00), 
        'stoptime': datetime(2015, 02, 07, 13, 00), \
        'location': 'Thomas Atkins', 'Type': 'Business Class'}]

