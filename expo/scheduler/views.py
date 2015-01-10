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
from scheduler.functions import tablePrep, event_info, day_to_cal_time
from scheduler.functions import set_time_format, conference_dates

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


def validate_perms(request, perms, require = True):
    '''
    Validate that the requesting user has the stated permissions
    Returns profile object if perms exist, False if not
    '''
    profile = validate_profile(request)
    if not profile:
        raise Http404
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    if require:                # error out if permission is required
        raise Http404
    return False               # or just return false if we're just checking

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

    confitems = event_class.objects
    if event_type=='Event':
        confitems = confitems.select_subclasses()
    else: 
        confitems = confitems.all()
    confitems = [item for item in confitems if item.schedule_ready]
    eventitems = []
    for ci in confitems:
        for sched_event in sorted(ci.eventitem_ptr.scheduler_events.all(), 
                                  key = lambda sched_event: sched_event.starttime):
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
    item = EventItem.objects.get_subclass(eventitem_id=eventitem_id)
    
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
    List of events (all, or by type)
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))
    if request.method == 'POST':
        event_type = request.POST['event_type']

    if event_type.strip() == '':
        template = 'scheduler/select_event_type.tmpl'
        event_type_options = list(set([ei.__class__.__name__ 
                                       for ei in EventItem.objects.all().select_subclasses()]))
        
        return render(request, template, {'type_options':event_type_options})

    header  = [ 'Title','Location','Date/Time','Duration','Type','Max Volunteer','Detail', 'Edit Schedule']
    events = get_events_display_info(event_type)


    template = 'scheduler/events_review_list.tmpl'
    return render(request, template, { 'events':events, 'header':header,
                                       'create_url': reverse('create_event', 
                                                urlconf='gbe.urls', 
                                                args=[event_type])})


def detail_view(request, eventitem_id):
    '''
    Takes the id of a single event_item and displays all its details in a template
    '''
    eventitem_view = get_event_display_info(eventitem_id)
    
    template = 'scheduler/event_detail.tmpl'
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
            l = LocationItem.objects.get_subclass(room__name = data['location'])
#            l = [l for l in LocationItem.objects.select_subclasses() if str(l) == data['location']][0]
            s_event.save()                        
            s_event.set_location(l)
            if data['teacher']:
                s_event.unallocate_role('Teacher')
                s_event.allocate_worker(data['teacher'].workeritem, 'Teacher')
            s_event.save()                        
            
            return HttpResponseRedirect(reverse('edit_event', 
                                                urlconf='scheduler.urls', 
                                                args=[event_type, scheduler_event_id]))
        else:
            raise Http404
    else:
        context =  {'user_id':request.user.id,
                    'event_id':scheduler_event_id}
        context['eventitem'] = get_event_display_info(item.eventitem.eventitem_id)
        context['tickets'] = context['eventitem']['event'].get_tickets  

        initial = {}
        initial['duration'] = item.duration
        initial['day'] = item.starttime.strftime("%Y-%m-%d")
        initial['time'] = item.starttime.strftime("%H:%M:%S")
        initial['location'] = item.location
        if item.event_type_name == 'Class':
            allocs = ResourceAllocation.objects.filter(event = item)
            workers = [Worker.objects.get(id = a.resource.id) for a in allocs if type(a.resource.item) == WorkerItem]
            teachers = [worker for worker in workers if worker.role == 'Teacher']

            if len(teachers) > 0:
                initial['teacher'] = teachers[0].item
            else:
                
                initial['teacher'] = item.as_subtype.teacher
                
        if validate_perms(request, ('Volunteer Coordinator',)):
            if item.event_type_name == 'GenericEvent' and item.as_subtype.type == 'Volunteer':
                context.update( get_worker_allocation_forms( item ) )
            else:
                context.update (get_manage_opportunity_forms (item, initial ) )
    context['form'] = EventScheduleForm(prefix = 'event', 
                                        instance=item,
                                        initial = initial)

    template = 'scheduler/event_schedule.tmpl'
#    foo()
    return render(request, template, context)


def get_manage_opportunity_forms( item, initial ):
    '''
    Generate the forms to allocate, edit, or delete volunteer opportunities associated with 
    a scheduler event. 
    '''
    from gbe.forms import VolunteerOpportunityForm
    actionform = []
    context = {}
    for opp in item.get_volunteer_opps():
        sevent = opp['sched']
        num_volunteers = sevent.max_volunteer
        day = sevent.start_time.strftime("%A")
        conf_date = conference_dates[day]
        time = sevent.start_time.time
        location = sevent.location
        if sevent.location:
            room = location.room
        else:
            room = item.location.room
        actionform.append(VolunteerOpportunityForm(instance=opp['conf'], 
                                                   initial = {'opp_event_id' : opp['conf'].event_id,
                                                              'opp_sched_id' : opp['sched'].id,
                                                              'num_volunteers' : num_volunteers, 
                                                              'day': conf_date,
                                                              'time': time, 
                                                              'location': room,
                                                              } ))
        context['actionform'] = actionform
                    
    createform =  VolunteerOpportunityForm (prefix='new_opp', initial = initial)
    actionheaders = ['Title', 
                     'Volunteer Type', 
                     'Volunteers Needed', 
                     'Duration', 
                     'Day', 
                     'Time', 
                     'Location', 
                     'Action' ]
    context.update ({  'createform':createform,
                     'actionheaders':actionheaders,})
    return context


def get_worker_allocation_forms( opp ):
    '''
    Returns a list of allocation forms for a volunteer opportunity
    Each form can be used to schedule one worker. Initially, must allocate one at a time. 
    '''
    allocations = ResourceAllocation.objects.filter(event=opp)
    allocs = ( alloc for alloc in allocations if 
               type(alloc.resource.item).__name__ == 'WorkerItem' and 
               type(alloc.resource.item.as_subtype).__name__  == 'Profile' ) 
    forms = [WorkerAllocationForm(initial = {'worker':alloc.resource.item.as_subtype, 
                                             'role':Worker.objects.get(id =alloc.resource.id).role,
                                             'label':alloc.get_label,
                                             'alloc_id':alloc.id})  
             for alloc in allocs]
    forms.append (WorkerAllocationForm(initial = {'role':'Volunteer', 'alloc_id' : -1}))
    return {'worker_alloc_forms':forms, 
            'worker_alloc_headers': ['Worker', 'Role', 'Notes'], 
            'opp_id': opp.id}

def allocate_workers(request, opp_id):
    '''
    Process a worker allocation form
    Needs a scheduler_event id
    '''
    if request.method != "POST":
        raise Http404

    opp = Event.objects.get(id = opp_id)
    form = WorkerAllocationForm(request.POST)

    if not form.is_valid():   # handle form errors
        raise Http404 
    
    data = form.cleaned_data
    worker = Worker(_item = data['worker'].workeritem, 
                    role = data['role'])
    worker.save()
    if data['alloc_id'] < 0:
        allocation = ResourceAllocation(event=opp, resource = worker)

    else:
        allocation = ResourceAllocation.objects.get(id = data['alloc_id'])
        allocation.resource = worker

    allocation.save()
    allocation.set_label(data['label'])

    return HttpResponseRedirect(reverse('edit_event', 
                                        urlconf='scheduler.urls', 
                                        args = [opp.event_type_name, opp_id]))


def manage_volunteer_opportunities(request, event_id):
    '''
    Create or edit volunteer opportunities for an event. 
    Volunteer opportunities are GenericEvents linked to Events by
    EventContainers, with a label of "Volunteer Shift". A volunteer 
    opportunity may schedule one person ("Follow spot operator") or 
    many ("Stage kittens"), but for clarity it should comprise a single
    role, which should be the "title" of the GenericEvent
    '''
    coordinator = validate_perms(request, ('Volunteer Coordinator',))
    from gbe.forms import VolunteerOpportunityForm
    from gbe.models import GenericEvent
    set_time_format()
    if request.method != 'POST':
        foo ()   # trigger error, for testing
        #return HttpResponseRedirect(reverse('edit_schedule', urlconf='scheduler.urls'))
    event = get_object_or_404(Event, id=event_id) 
    
    if 'create' in request.POST.keys():  # creating a new opportunity
        form = VolunteerOpportunityForm(request.POST, prefix = 'new_opp')
        
        if form.is_valid():                                                          
            opp = form.save(commit = False)
            opp.type = "Volunteer"
            opp.save()
            data = form.cleaned_data
            day = data.get('day')
            time = data.get('time')
            day = ' '.join([day.split(' ') [0], time])
            start_time = datetime.strptime(day, "%Y-%m-%d %H:%M:%S")
            
                           
            opp_event = Event(eventitem = opp.eventitem_ptr,
                              max_volunteer = data.get('num_volunteers', 1), 
                              starttime = start_time,
                              location = data.get('location').locationitem,
                              duration = data.get('duration'))
            opp_event.save()
            container = EventContainer(parent_event = event, child_event=opp_event)
            container.save()
        else:
            errors = form.errors
            bar()
    elif 'delete' in request.POST.keys():  #delete this opportunity
        opp = get_object_or_404(GenericEvent, event_id = request.POST['opp_event_id'])
        opp.delete()


    elif 'edit' in request.POST.keys():   # edit this opportunity
        opp = get_object_or_404(GenericEvent, event_id = request.POST['opp_event_id'])
        opp_event_container = EventContainer.objects.get(child_event=request.POST['opp_sched_id'])
        opp_event = Event.objects.get(id=request.POST['opp_sched_id'])
        form = VolunteerOpportunityForm(request.POST, instance=opp)
        if not form.is_valid():
            raise Http404
        form.save()
        data = form.cleaned_data
        opp_event.max_volunteer = data['num_volunteers']
        
        day = data.get('day')
        time = data.get('time')
        day = ' '.join([day.split(' ') [0], time])
        start_time = datetime.strptime(day, "%Y-%m-%d %H:%M:%S")

        opp_event.starttime = start_time
        opp_event.save()
        opp_event.set_location (data.get('location').locationitem)
        opp_event.save()
#        foo()
    elif 'allocate' in request.POST.keys():   # forward this to allocate view
        return HttpResponseRedirect(reverse('edit_event', urlconf='scheduler.urls', 
                                    args = ['GenericEvent',  request.POST['opp_sched_id']]))


    else:
        foo()  # trigger error so I can see the locals
    return HttpResponseRedirect(reverse('edit_event', 
                                        urlconf='scheduler.urls', 
                                        args = [event.event_type_name, event_id]))
        
        
        

def contact_info(request, event_id=None, resource_type = 'All', status=None, worker_type=None):
    '''
    Return contact info (email addresses) for a scheduler.Event. Currently configured for shows only
    '''
    import csv
    event = Event.objects.get(schedulable_ptr_id = event_id)
    data = event.contact_info(resource_type, status, worker_type)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s_contacts.csv' % str(event).replace(' ','_')
    writer = csv.writer(response)
    writer.writerow(['Name', 'email'])
    for row in data:
        writer.writerow(row)
    return response
    

def add_event(request, eventitem_id, event_type='class'):
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


def manage_rehearsals(request, event_id):
    '''
    handler for rehearsal slot manage calls
    TODO
    '''
    pass
        


def calendar_view(request = None,
        event_type = 'Show',
        day = None,
        cal_times = (datetime(2015, 02, 21, 8, 00, 
                tzinfo=pytz.timezone('UTC')),
            datetime(2015, 02, 22, 4, 00, 
                tzinfo=pytz.timezone('UTC'))),
        time_format=None,
        duration = Duration(minutes = 30)):
    '''
    A view to query the database for events of type cal_type over the period of time cal_times,
    and turn the information into a calendar in block format for display.
    Or it will be, eventually.  Right now it is using dummy event information for testing purposes.
    Will add in database queries once basic funcationality is completed.
    '''

    if day != None:
        cal_times = day_to_cal_time(day, week = datetime(2015, 02, 19,tzinfo=pytz.timezone('UTC')))
    events = event_info(confitem_type = event_type, cal_times = cal_times)

    if time_format == None:
        time_format = set_time_format()

    ###  Changing function to get table labels from the request
    Table = {}
    Table['rows'] = tablePrep(events, duration, cal_start = cal_times[0], cal_stop = cal_times[1])
    Table['name'] = 'Event Calendar for the Great Burlesque Expo of 2015'
    Table['link'] = 'http://burlesque-expo.com'
    Table['x_name'] = {}
    Table['x_name']['html'] = 'Rooms'
    Table['x_name']['link'] = 'http://burlesque-expo.com/class_rooms'   ## Fix This!!!

    template = 'scheduler/Sched_Display.tmpl'

    return render(request, template, Table)
