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


def get_events_display_info(event_type = 'Class', time_format = None):
    '''
    Helper for displaying lists of events. Gets a supply of conference event items and munges 
    them into displayable shape
    "Conference event items" = things in the conference model which extend EventItems and therefore 
    could be Events
    '''
    import gbe.models as gbe
    if time_format == None: time_format = set_time_format(days = 2)
    event_class = eval('gbe.' + event_type)

    confitems = event_class.objects.all()
    confitems = [item for item in confitems if item.schedule_ready]
    eventitems = [{ 'eventitem': ci.eventitem_ptr , 
                  'confitem':ci,
                  'schedule_event':ci.eventitem_ptr.scheduler_events.all().first()}
                  for ci in confitems]

                    

    eventslist = []
    for entry in eventitems:
        eventinfo = {'title' : entry['confitem'].sched_payload['title'],
                'duration': entry['confitem'].sched_payload['duration'],
                    'type':entry['confitem'].sched_payload['details']['type'],
                    'detail': reverse('detail_view', 
                                      urlconf='scheduler.urls', 
                                      args = [entry['eventitem'].eventitem_id]),
                    'edit': reverse('edit_event', 
                                    urlconf='scheduler.urls', 
                                    args =  [event_type,  entry['eventitem'].eventitem_id]),
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

    


@login_required
def event_list(request, event_type=''):
    '''
    List of events (all)
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))
    if request.method == 'POST':
        event_type = request.POST['event_type']

    if event_type.strip() == '':
        template = 'scheduler/select_event_type.tmpl'
        event_type_options = list(set([ei.__class__.__name__ for ei in EventItem.objects.all().select_subclasses()]))
        
        return render(request, template, {'type_options':event_type_options})

    header  = [ 'Title','Location','Date/Time','Duration','Type','Max Volunteer','Detail', 'Edit Schedule']
    events = get_events_display_info(event_type)


    template = 'scheduler/events_review_list.tmpl'
    return render(request, template, { 'events':events, 'header':header})


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


def schedule_acts(request):
    '''
    Display a list of acts available for scheduling, allows setting show/order
    '''
    validate_perms(request, ('Scheduling Mavens',))
    show_title = ''

    if request.method=="POST":
        import gbe.models as conf
        show_title = request.POST.get('event_type', 'POST')   # figure out where we're coming from

#        foo()

    if show_title.strip() == '' :
        
        import gbe.models as conf
        template = 'scheduler/select_event_type.tmpl'
        show_options = EventItem.objects.all().select_subclasses()
        show_options = filter( lambda event: type(event)==conf.Show, show_options)
        return render(request, template, {'type_options':show_options})        


    if show_title == 'POST':      # we're coming from an ActSchedulerForm
#        foo()  # trigger error so I can see the post....
        alloc_prefixes = set([key.split('-')[0] for key in request.POST.keys()
                      if key.startswith('allocation_')])
        for prefix in alloc_prefixes:
            form = ActScheduleForm(request.POST, prefix=prefix)
            if form.is_valid():
                data = form.cleaned_data
            else:
                continue  # error, should log
            alloc = get_object_or_404(ResourceAllocation, id = prefix.split('_')[1])

            alloc.event =  data['show']
            alloc.save()
            ordering = alloc.ordering
            ordering.order = data['order']
            ordering.save()
        return HttpResponseRedirect(reverse('home', urlconf = 'gbe.urls'))

    # we should have a show title at this point. 

    show = conf.Show.objects.get(title = show_title)
            
    import gbe.models as conf
    # get allocations involving the show we want
    event = show.scheduler_events.first()


    allocations = ResourceAllocation.objects.filter(event=event)
    allocations = [a for a in allocations if type(a.resource.item) == ActItem]


    forms = []
    for alloc in allocations:
        actitem = alloc.resource.item
        if type (actitem) != ActItem:
            continue
        act = actitem.act
        details = {}
        details ['title'] = act.title
        details ['performer'] = act.performer
        details ['show'] = event
        details ['order'] = alloc.ordering.order
        details ['actresource'] = alloc.resource.id

        
        forms.append( [details, alloc] )
    forms = sorted(forms, key = lambda f: f[0]['order'])
    
    forms = [ActScheduleForm(initial=details, prefix = 'allocation_'+str(alloc.id))
             for (details, alloc) in forms]

    template = 'scheduler/act_schedule.tmpl'
    return render (request, 
                   template, 
                   {'forms':forms})
    


def edit_event(request, eventitem_id, event_type='class'):
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
            
            return HttpResponseRedirect(reverse('event_schedule', 
                                                urlconf='scheduler.urls', 
                                                args=[event_type]))
        else:
            raise Http404
    else:
        old_events = item.scheduler_events.all()
        duration = item.event.sched_payload['duration']
        if len(old_events) > 0:
            event = old_events[0]
            day = event.starttime.strftime("%A")
            time = event.starttime.strftime("%H:%M")
            location = event.location
            form = EventScheduleForm(prefix = "event", instance=event,
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
            items = GenericEvent.objects.filter(type=event_type).order_by('title')
        elif class_types.has_key(event_type):
            items = Class.objects.filter(accepted='3', type=event_type).order_by('title')
        elif event_type=='Show':
            items = Show.objects.all()
        elif event_type=='Class':
            items = Class.objects.filter(accepted='3').exclude(type='Panel').order_by('title')
        else:
            items = EventItem.objects.all().select_subclasses().order_by('title')
            event_type="All"

        events = [{'eventitem': item, 
                    'scheduled_events':item.scheduler_events.all(),
                    'detail': reverse('detail_view', 
                                      urlconf='scheduler.urls', 
                                      args = [item.eventitem_id])}
                    for item in items]
    except:
        events = None
    return render(request, 'scheduler/event_display_list.tmpl',
                  {'title': list_titles[event_type],
                   'view_header_text': list_text[event_type],
                   'labels': event_labels,
                   'events': events})



def calendar_view(request, 
                  cal_type = 'Event', 
                  cal_times = (datetime(2015, 02, 20, 18, 00), 
                               datetime(2015, 02, 23, 00,00)), 
                  time_format=None):

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

