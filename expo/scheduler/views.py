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
    eventitems = []
    for ci in confitems:
        for sched_event in sorted(ci.eventitem_ptr.scheduler_events.all(), key = lambda sched_event: sched_event.starttime):
            eventitems += [{ 'eventitem': ci.eventitem_ptr , 
                             'confitem':ci,
                             'schedule_event':sched_event}]
        else:
            eventitems += [{ 'eventitem': ci.eventitem_ptr , 
                             'confitem':ci,
                             'schedule_event':None}]

                    

    eventslist = []
    for entry in eventitems:
        eventinfo = {'title' : entry['confitem'].sched_payload['title'],
                    'duration': entry['confitem'].sched_payload['duration'],
                    'type':entry['confitem'].sched_payload['details']['type'],
                    'detail': reverse('detail_view', 
                                      urlconf='scheduler.urls', 
                                      args = [entry['eventitem'].eventitem_id]),
                    }
        if entry['schedule_event']:
            eventinfo ['edit'] = reverse('edit_event', urlconf='scheduler.urls', 
                                         args =  [event_type,  entry['schedule_event'].id])
            eventinfo ['location'] = entry['schedule_event'].location
            eventinfo ['datetime'] =  entry['schedule_event'].starttime.strftime(time_format)
            eventinfo ['max_volunteer'] =  entry['schedule_event'].max_volunteer
        else:
            eventinfo ['create'] = reverse('create_event', urlconf='scheduler.urls', 
                                         args =  [event_type,  entry['eventitem'].eventitem_id])
            eventinfo ['location'] = None
            eventinfo ['datetime'] = None
            eventinfo ['max_volunteer'] =  None
        eventslist.append(eventinfo)

    return eventslist

def get_event_display_info(eventitem_id):
    '''
    Helper for displaying a single of event. Same idea as get_events_display_info - but for
    only one eventitem.  
    '''
    item = EventItem.objects.filter(eventitem_id=eventitem_id).select_subclasses().first()
    
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
        if act.accepted != 3:
            continue
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
    


def edit_event(request, scheduler_event_id, event_type='class'):
    '''
    Add an item to the conference schedule and/or set its schedule details (start
    time, location, duration, or allocations)
    Takes a scheduler.Event id 
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))

    try:
        item = Event.objects.get_subclass(id = scheduler_event_id)
    except:
        raise Exception ("Error code XYZZY: Couldn't get an item for id")
    
    if request.method=='POST':
        event_form = EventScheduleForm(request.POST, 
                                       instance = item,
                                       prefix='event')
        if (event_form.is_valid()  and True):

            s_event=event_form.save(commit=False)
            data = event_form.cleaned_data
                         
            if data['duration']:
                s_event.set_duration(data['duration'])
                
            l = [l for l in LocationItem.objects.select_subclasses() if str(l) == data['location']][0]
            s_event.save()                        
            s_event.set_location(l)
            if data['teacher']:
                s_event.unallocate_role('Teacher')
                s_event.allocate_worker(data['teacher'].workeritem, 'Teacher')
            s_event.save()                        
            
            return HttpResponseRedirect(reverse('event_schedule', 
                                                urlconf='scheduler.urls', 
                                                args=[event_type]))
        else:
            raise Http404
    else:

        initial = {}
        initial['duration'] = item.duration
        initial['day'] = item.starttime.strftime("%Y-%m-%d")
        initial['time'] = item.starttime.strftime("%H:%M:%S")
        initial['location'] = item.location
        allocs = ResourceAllocation.objects.filter(event = item)
        workers = [Worker.objects.get(id = a.resource.id) for a in allocs if type(a.resource.item) == WorkerItem]
        teachers = [worker for worker in workers if worker.role == 'Teacher']
        if len(teachers) > 0:
            initial['teacher'] = teachers[0].item ## to do: handle multiple teachers

        form = EventScheduleForm(prefix = "event", 
                                 instance=item,
                                 initial = initial)
    template = 'scheduler/event_schedule.tmpl'
    eventitem_view = get_event_display_info(item.eventitem.eventitem_id)
    return render(request, template, {'eventitem': eventitem_view,
                                      'form': form,
                                      'show_tickets': True,
                                      'tickets': eventitem_view['event'].get_tickets,
                                      'user_id':request.user.id})

def create_event(request, eventitem_id, event_type='class'):
    '''
    Add an item to the conference schedule and/or set its schedule details (start
    time, location, duration, or allocations)
    Takes a scheduler.EventItem id - BB - separating new event from editing existing, so that
    edit can identify particular schedule items, while this identifies the event item.
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))

    try:
        item = EventItem.objects.get_subclass(eventitem_id = eventitem_id)
    except:
        raise Exception ("Error code XYZZY: Couldn't get an item for id")
    
    if request.method=='POST':
        event_form = EventScheduleForm(request.POST, 
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
        duration = item.duration
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


def event_info(confitem_type = 'Show', cal_times= (datetime(2015, 02, 20, 18, 00),
        datetime(2015, 02, 23, 00, 00))):
    '''
    Queries the database for scheduled events of type confitem_type, during time cal_times,
    and returns their important information in a dictionary format.
    '''

    import gbe.models as conf
    from scheduler.models import Location
    
    if confitem_type=='All':
        confitems_list = conf.Event.objects.all()
    else:
        confitem_class = eval ('conf.'+confitem_type)
        confitems_list = confitem_class.objects.all()
        
    confitems_list = [confitem for confitem in confitems_list if confitem.schedule_ready]

    loc_allocs = []
    for l in Location.objects.all():
        loc_allocs += l.allocations.all()

    scheduled_events = [alloc.event for alloc in loc_allocs]
    # for event in scheduled_events: filter on start_time and stop_time vs cal_times
    scheduled_event_ids = [alloc.event.eventitem_id for alloc in scheduled_events]    

    events_dict = {}
    for index in range(len(scheduled_event_ids)):
        for confitem in confitems_list:
            if scheduled_event_ids[index] == confitem.eventitem_id:
                events_dict[scheduled_events[index]] = confitem

    events = [{'title': confitem.title,
               'link' : reverse('detail_view', urlconf='scheduler.urls', 
                   args = [str(confitem.eventitem_id)]), # could also be event_id, doublecheck
               'description': confitem.description,
               'start_time':  event.start_time,
               'stop_time':  event.start_time + confitem.duration,
               'location' : event.location.room.name,
            }
        for (event, confitem) in events_dict.items()]

    return events

#def calendar_view(request, 
def calendar_view(request = None,
        event_type = 'Show', cal_times= (datetime(2015, 02, 20, 18, 00),
        datetime(2015, 02, 23, 00, 00)), time_format=None,
        duration = Duration(minutes = 30)):
    '''
    A view to query the database for events of type cal_type over the period of time cal_times,
    and turn the information into a calendar in block format for display.

    Or it will be, eventually.  Right now it is using dummy event information for testing purposes.
    Will add in database queries once basic funcationality is completed.
    '''

    events = event_info(event_type, cal_times)

    if time_format == None:
        time_format = set_time_format()

    ###  Changing function to get table labels from the request
    Table = {}
    Table['rows'] = tablePrep(events, duration)
    Table['name'] = 'Event Calendar for the Great Burlesque Expo of 2015'
    Table['link'] = 'http://burlesque-expo.com'
    Table['x_name'] = {}
    Table['x_name']['html'] = 'Rooms'
    Table['x_name']['link'] = 'http://burlesque-expo.com/class_rooms'   ## Fix This!!!

    template = 'scheduler/Sched_Display.tmpl'

    return render(request, template, Table)
    
def faux_event_info(event_type = 'Show', cal_times= (datetime(2015, 02, 20, 18, 00),
        datetime(2015, 02, 23, 00, 00))):
    '''
    Return event info as if a db query had been issued.
    '''

    return [{'html': 'Horizontal Pole Dancing 101', 'Link': 'http://some.websi.te', \
        'start_time': datetime(2015, 02, 07, 9, 00), 
        'stop_time': datetime(2015, 02, 07, 10, 00), \
        'location': 'Paul Revere', 'Type': 'Movement Class'}, 

    {'html': 'Shimmy Shimmy, Shake', 'Link': 'http://some.new.websi.te', \
        'start_time': datetime(2015, 02, 07, 13, 00), 
        'stop_time': datetime(2015, 02, 07, 14, 00), \
        'location': 'Paul Revere', 'Type': 'Movement Class'},

    {'html': 'Jumpsuit Removes', 'Link': 'http://some.other.websi.te', \
        'start_time': datetime(2015, 02, 07, 10, 00), 
        'stop_time': datetime(2015, 02, 07, 11, 00), \
        'location': 'Paul Revere', 'Type': 'Movement Class'},

    {'html': 'Tax Dodging for Performers', 'Link': 'http://yet.another.websi.te', \
        'start_time': datetime(2015, 02, 07, 11, 00), 
        'stop_time': datetime(2015, 02, 07, 12, 00), \
        'location': 'Paul Revere', 'Type': 'Business Class'},

    {'html': 'Butoh Burlesque', 'Link': 'http://japanese.websi.te', \
        'start_time': datetime(2015, 02, 07, 9, 00), 
        'stop_time': datetime(2015, 02, 07, 10, 00), \
        'location': 'Thomas Atkins', 'Type': 'Movement Class'},

    {'html': 'Kick Left, Kick Face, Kick Ass: Burly-Fu', \
        'Link': 'http://random.new.websi.te', \
        'start_time': datetime(2015, 02, 07, 14, 00), 
        'stop_time': datetime(2015, 02, 07, 16, 00),\
        'location': 'Thomas Atkins', 'Type': 'Movement Class'},

    {'html': 'Muumuus A-Go-Go', 'short_desc': 'Dancing in Less-then-Sexy Clothing', \
        'Link': 'http://some.bad.websi.te', \
        'start_time': datetime(2015, 02, 07, 10, 00), 
        'stop_time': datetime(2015, 02, 07, 12, 00), \
        'location': 'Thomas Atkins', 'Type': 'Movement Class'},

    {'html': 'From Legalese to English, Contracts in Burlesque', \
        'Link': 'http://still.another.websi.te', \
        'start_time': datetime(2015, 02, 07, 12, 00), 
        'stop_time': datetime(2015, 02, 07, 13, 00), \
        'location': 'Thomas Atkins', 'Type': 'Business Class'}]

