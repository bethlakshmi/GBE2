from django.shortcuts import (
    render,
    get_object_or_404,
    render_to_response,
)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    Http404,
)
from django.db.models import (
    Q,
    Count,
)
from django.contrib.auth.forms import UserCreationForm
from django.template import (
    loader,
    RequestContext,
)
from scheduler.models import *
from scheduler.forms import *
from gbe.forms import VolunteerOpportunityForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    login,
    logout,
    authenticate,
)
from django.forms.models import inlineformset_factory
from django.core.urlresolvers import reverse
from datetime import datetime
from datetime import time as dttime
import pytz
import csv

from table import table
from gbe_forms_text import (
    volunteer_interests_options,
    list_titles,
)
from gbetext import acceptance_states
from gbe.duration import (
    Duration,
    DateTimeRange,
)
from functions import (
    table_prep,
    event_info,
    day_to_cal_time,
    cal_times_for_conf,
    overlap_clear,
    set_time_format,
    conference_dates,
)
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    get_conference_day,
    validate_perms,
    validate_profile,
    get_events_list_by_type,
    conference_list,
    available_volunteers,
)


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


def get_events_display_info(event_type='Class', time_format=None):
    '''
    Helper for displaying lists of events. Gets a supply of conference event
    items and munges them into displayable shape
    "Conference event items" = things in the conference model which extend
    EventItems and therefore
    could be Events
    '''
    import gbe.models as gbe
    if time_format is None:
        time_format = set_time_format(days=2)
    event_class = eval('gbe.' + event_type)
    conference = gbe.Conference.current_conf()
    confitems = event_class.objects.filter(visible=True,
                                           conference=conference)
    if event_type == 'Event':
        confitems = confitems.select_subclasses()
    else:
        confitems = confitems.all()
    confitems = [item for item in confitems if item.schedule_ready]
    eventitems = []
    for ci in confitems:
        for sched_event in sorted(
                ci.eventitem_ptr.scheduler_events.all(),
                key=lambda sched_event: sched_event.starttime):
            eventitems += [{'eventitem': ci.eventitem_ptr,
                            'confitem': ci,
                            'schedule_event': sched_event}]
        else:
            eventitems += [{'eventitem': ci.eventitem_ptr,
                            'confitem': ci,
                            'schedule_event': None}]

    eventslist = []
    for entry in eventitems:
        if ('type' not in entry['confitem'].sched_payload['details'].keys() or
                entry['confitem'].sched_payload['details']['type'] == ''):
                entry['confitem'].sched_payload['details']['type'] = \
                    entry['confitem'].type
        eventinfo = {'title': entry['confitem'].sched_payload['title'],
                     'duration': entry['confitem'].sched_payload['duration'],
                     'type': entry['confitem'].sched_payload['details']
                                              .get('type', ''),
                     'detail': reverse('detail_view',
                                       urlconf='scheduler.urls',
                                       args=[entry['eventitem'].eventitem_id])}

        if entry['schedule_event']:
            eventinfo['edit'] = reverse('edit_event',
                                        urlconf='scheduler.urls',
                                        args=[event_type,
                                              entry['schedule_event'].id])
            eventinfo['location'] = entry['schedule_event'].location
            eventinfo['datetime'] = entry['schedule_event'].starttime.strftime(
                time_format)
            eventinfo['max_volunteer'] = entry['schedule_event'].max_volunteer
            eventinfo['volunteer_count'] = entry[
                'schedule_event'].volunteer_count
            eventinfo['delete'] = reverse('delete_schedule',
                                          urlconf='scheduler.urls',
                                          args=[entry['schedule_event'].id])

        else:
            eventinfo['create'] = reverse(
                'create_event',
                urlconf='scheduler.urls',
                args=[event_type,
                      entry['eventitem'].eventitem_id])
            eventinfo['delete'] = reverse(
                'delete_event',
                urlconf='scheduler.urls',
                args=[event_type, entry['eventitem'].eventitem_id])
            eventinfo['location'] = None
            eventinfo['datetime'] = None
            eventinfo['max_volunteer'] = None
        eventslist.append(eventinfo)
    return eventslist


def get_event_display_info(eventitem_id):
    '''
    Helper for displaying a single of event. Same idea as
    get_events_display_info - but for
    only one eventitem.
    '''
    try:
        item = EventItem.objects.get_subclass(eventitem_id=eventitem_id)
    except EventItem.DoesNotExist:
        raise Http404
    bio_grid_list = []
    for sched_event in item.scheduler_events.all():
        bio_grid_list += sched_event.bio_list
    eventitem_view = {'event': item,
                      'scheduled_events': item.scheduler_events.all().order_by(
                          'starttime'),
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
        event_type_options = list(
            set([ei.__class__.__name__
                 for ei in EventItem.objects.filter(
                         visible=True).select_subclasses()]))
        return render(request,
                      template,
                      {'type_options': event_type_options})

    header = ['Title',
              'Location',
              'Date/Time',
              'Duration',
              'Type',
              'Max Volunteer',
              'Current Volunteer',
              'Detail',
              'Edit Schedule',
              'Delete']
    events = get_events_display_info(event_type)

    template = 'scheduler/events_review_list.tmpl'
    return render(request,
                  template,
                  {'events': events,
                   'header': header,
                   'create_url': reverse('create_event',
                                         urlconf='gbe.urls',
                                         args=[event_type])})


def detail_view(request, eventitem_id):
    '''
    Takes the id of a single event_item and displays all its
    details in a template
    '''
    eventitem_view = get_event_display_info(eventitem_id)

    template = 'scheduler/event_detail.tmpl'
    return render(request,
                  template,
                  {'eventitem': eventitem_view,
                   'show_tickets': True,
                   'tickets': eventitem_view['event'].get_tickets,
                   'user_id': request.user.id}
                  )


def schedule_acts(request, show_title=None):
    '''
    Display a list of acts available for scheduling, allows setting show/order
    '''
    validate_perms(request, ('Scheduling Mavens',))
    import gbe.models as conf

    if request.method == "POST":
        show_title = request.POST.get('event_type', 'POST')

    if show_title.strip() == '':
        import gbe.models as conf
        template = 'scheduler/select_event_type.tmpl'
        show_options = EventItem.objects.all().select_subclasses()
        show_options = filter(lambda event: type(event) == conf.Show,
                              show_options)
        return render(request, template, {'type_options': show_options})

    if show_title == 'POST':      # we're coming from an ActSchedulerForm
        alloc_prefixes = set([key.split('-')[0] for key in request.POST.keys()
                              if key.startswith('allocation_')])
        for prefix in alloc_prefixes:
            form = ActScheduleForm(request.POST, prefix=prefix)
            if form.is_valid():
                data = form.cleaned_data
            else:
                continue  # error, should log
            alloc = get_object_or_404(ResourceAllocation,
                                      id=prefix.split('_')[1])

            alloc.event = data['show']
            alloc.save()
            ordering = alloc.ordering
            ordering.order = data['order']
            ordering.save()
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    # we should have a show title at this point.

    show = conf.Show.objects.get(title=show_title)
    import gbe.models as conf
    # get allocations involving the show we want
    event = show.scheduler_events.first()

    allocations = ResourceAllocation.objects.filter(event=event)
    allocations = [a for a in allocations if type(a.resource.item) == ActItem]

    forms = []
    for alloc in allocations:
        actitem = alloc.resource.item
        if type(actitem) != ActItem:
            continue
        act = actitem.act
        if act.accepted != 3:
            continue
        details = {}
        details['title'] = act.title
        details['performer'] = act.performer
        details['show'] = event
        try:
            details['order'] = alloc.ordering.order
        except:
            o = Ordering(allocation=alloc, order=0)
            o.save()
            details['order'] = 0
        details['actresource'] = alloc.resource.id

        forms.append([details, alloc])
    forms = sorted(forms, key=lambda f: f[0]['order'])
    forms = [ActScheduleForm(initial=details,
                             prefix='allocation_'+str(alloc.id))
             for (details, alloc) in forms]

    template = 'scheduler/act_schedule.tmpl'
    return render(request,
                  template,
                  {'forms': forms})


def delete_schedule(request, scheduler_event_id):
    '''
    Remove the scheduled item
    '''
    event = get_object_or_404(Event, id=scheduler_event_id)
    type = event.event_type_name
    event.delete()
    return HttpResponseRedirect(reverse('event_schedule',
                                        urlconf='scheduler.urls',
                                        args=[type]))


def delete_event(request, eventitem_id, event_type):
    '''
    Remove any scheduled items, make basic event item invisible
    '''
    event = get_object_or_404(EventItem, eventitem_id=eventitem_id)
    event.remove()
    return HttpResponseRedirect(reverse('event_schedule',
                                        urlconf='scheduler.urls',
                                        args=[event_type]))


def get_manage_opportunity_forms(item, initial, errorcontext=None):
    '''
    Generate the forms to allocate, edit, or delete volunteer
    opportunities associated with a scheduler event.
    '''
    actionform = []
    context = {}
    for opp in item.get_volunteer_opps():
        if (errorcontext and
                'error_opp_form' in errorcontext and
                errorcontext['error_opp_form'].instance == opp['conf']):
            actionform.append(errorcontext['error_opp_form'])
        else:
            sevent = opp['sched']
            num_volunteers = sevent.max_volunteer
            date = sevent.start_time.date()
            conference = opp['conf'].conference

            time = sevent.start_time.time
            day = get_conference_day(conference=conference,
                                     date=date)
            location = sevent.location
            if location:
                room = location.room
            else:
                room = item.location.room
            actionform.append(
                VolunteerOpportunityForm(
                    instance=opp['conf'],
                    initial={'opp_event_id': opp['conf'].event_id,
                             'opp_sched_id': opp['sched'].id,
                             'num_volunteers': num_volunteers,
                             'day': day,
                             'time': time,
                             'location': room,
                             },
                    conference=conference
                )
            )
    context['actionform'] = actionform
    if errorcontext and 'createform' in errorcontext:
        createform = errorcontext['createform']
    else:
        createform = VolunteerOpportunityForm(
            prefix='new_opp',
            initial=initial,
            conference=item.eventitem.get_conference())

    actionheaders = ['Title',
                     'Volunteer Type',
                     '#',
                     'Duration',
                     'Day',
                     'Time',
                     'Location']
    context.update({'createform': createform,
                    'actionheaders': actionheaders})
    return context


def get_worker_allocation_forms(opp, errorcontext=None):
    '''
    Returns a list of allocation forms for a volunteer opportunity
    Each form can be used to schedule one worker. Initially, must
    allocate one at a time.
    '''
    allocations = ResourceAllocation.objects.filter(event=opp)
    allocs = (alloc for alloc in allocations if
              type(alloc.resource.item).__name__ == 'WorkerItem' and
              type(alloc.resource.item.as_subtype).__name__ == 'Profile')
    forms = []
    for alloc in allocs:
        if (errorcontext and
                worker_alloc_forms in errorcontext and
                errorcontext['worker_alloc_forms'].cleaned_data[
                    'alloc_id']) == alloc.id:
            forms.append(errorcontext['worker_alloc_forms'])
        else:
            forms.append(WorkerAllocationForm(
                initial={'worker': alloc.resource.item.as_subtype,
                         'role': Worker.objects.get(
                             id=alloc.resource.id).role,
                         'label': alloc.get_label,
                         'alloc_id': alloc.id}
                )
            )
    if errorcontext and 'new_worker_alloc_form' in errorcontext:
        forms.append(errorcontext['new_worker_alloc_form'])
    forms.append(WorkerAllocationForm(initial={'role': 'Volunteer',
                                               'alloc_id': -1}))
    return {'worker_alloc_forms': forms,
            'worker_alloc_headers': ['Worker', 'Role', 'Notes'],
            'opp_id': opp.id}


def show_potential_workers(opp):
    '''
    Get lists of potential workers for this opportunity. These will be
    inserted into the edit_event template directly.
    Returns a dictionary, we'll update the context dictionary on return
    Opp is a sched.Event
    '''
    import gbe.models as conf
    interested = list(conf.Volunteer.objects.filter(
        interests__contains=opp.as_subtype.volunteer_category))
    all_volunteers = list(conf.Volunteer.objects.all())
    available = available_volunteers(opp.start_time)
    return {'interested_volunteers': interested,
            'all_volunteers': all_volunteers,
            'available_volunteers': available}


def allocate_workers(request, opp_id):
    '''
    Process a worker allocation form
    Needs a scheduler_event id
    '''
    if request.method != "POST":
        raise Http404
    opp = Event.objects.get(id=opp_id)
    form = WorkerAllocationForm(request.POST)

    if not form.is_valid():
        try:
            ResourceAllocation.objects.get(id=data['alloc_id'])
            return edit_event_display(request,
                                      opp,
                                      {'worker_alloc_forms': form})
        except:
            form.alloc_id = -1
            return edit_event_display(request,
                                      opp,
                                      {'new_worker_alloc_form': form})
    data = form.cleaned_data
    # if no worker, the volunteer that was there originally is deallocated.
    if 'delete' in request.POST.keys():
        alloc = ResourceAllocation.objects.get(id=request.POST['alloc_id'])
        res = alloc.resource
        alloc.delete()
        res.delete()
    elif data.get('worker', None):
        worker = Worker(_item=data['worker'].workeritem,
                        role=data['role'])
        worker.save()
        if data['alloc_id'] < 0:
            allocation = ResourceAllocation(event=opp,
                                            resource=worker)
        else:
            allocation = ResourceAllocation.objects.get(id=data['alloc_id'])
            allocation.resource = worker
        allocation.save()
        allocation.set_label(data['label'])

    return HttpResponseRedirect(reverse('edit_event',
                                        urlconf='scheduler.urls',
                                        args=[opp.event_type_name, opp_id]))


@login_required
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
    from gbe.models import GenericEvent
    set_time_format()
    template = 'scheduler/event_schedule.tmpl'

    event = get_object_or_404(Event, id=event_id)

    if request.method != 'POST':
        # TO DO: review this
        return HttpResponseRedirect(reverse('edit_event',
                                    urlconf='scheduler.urls',
                                    args=[event.event_type_name,
                                          event_id]))
    if 'create' in request.POST.keys() or 'duplicate' in request.POST.keys():
        if 'create' in request.POST.keys():
            form = VolunteerOpportunityForm(
                request.POST,
                prefix='new_opp',
                conference=event.eventitem.get_conference())
        else:
            form = VolunteerOpportunityForm(
                request.POST,
                conference=event.eventitem.get_conference())
        if form.is_valid():
            opp = form.save(commit=False)
            opp.type = "Volunteer"
            opp.conference = event.eventitem.get_conference()
            opp.save()
            data = form.cleaned_data
            day = data.get('day').day
            time_parts = map(int, data.get('time').split(":"))
            start_time = datetime.combine(day, dttime(*time_parts,
                                                      tzinfo=pytz.utc))
            opp_event = Event(eventitem=opp.eventitem_ptr,
                              max_volunteer=data.get('num_volunteers', 1),
                              starttime=start_time,
                              duration=data.get('duration'))
            opp_event.save()

            opp_event.set_location(data.get('location').locationitem)
            opp_event.save()
            container = EventContainer(parent_event=event,
                                       child_event=opp_event)
            container.save()
        else:
            errors = form.errors
            return edit_event_display(request, event, {'createform': form})
    elif 'delete' in request.POST.keys():
        opp = get_object_or_404(GenericEvent,
                                event_id=request.POST['opp_event_id'])
        opp.delete()
    elif 'edit' in request.POST.keys():
        opp = get_object_or_404(GenericEvent,
                                event_id=request.POST['opp_event_id'])
        opp_event_container = EventContainer.objects.get(
            child_event=request.POST['opp_sched_id'])
        opp_event = Event.objects.get(id=request.POST['opp_sched_id'])
        form = VolunteerOpportunityForm(request.POST,
                                        instance=opp,
                                        conference=opp.conference)
        if not form.is_valid():
            return edit_event_display(request, event, {'error_opp_form': form})

        form.save()
        data = form.cleaned_data
        opp_event.max_volunteer = data['num_volunteers']
        day = data.get('day').day
        time_parts = map(int, data.get('time').split(":"))
        start_time = datetime.combine(day,
                                      dttime(*time_parts, tzinfo=pytz.utc))
        opp_event.starttime = start_time
        opp_event.save()
        opp_event.set_location(data.get('location').locationitem)
        opp_event.save()
    elif 'allocate' in request.POST.keys():
        return HttpResponseRedirect(reverse('edit_event',
                                            urlconf='scheduler.urls',
                                    args=['GenericEvent',
                                            request.POST['opp_sched_id']]))
    return HttpResponseRedirect(reverse('edit_event',
                                        urlconf='scheduler.urls',
                                        args=[event.event_type_name,
                                                event_id]))


def contact_info(request,
                 event_id=None,
                 resource_type='All',
                 status=None,
                 worker_type=None):
    '''
    Return contact info (email addresses) for a scheduler.Event.
    Currently configured for shows only
    '''
    validate_perms(request, ('Act Coordinator',
                             'Class Coordinator',
                             'Volunteer Coordinator',
                             'Scheduling Mavens',
                             'Vendor Coordinator'),
                   require=True)
    event = Event.objects.get(schedulable_ptr_id=event_id)
    data = event.contact_info(resource_type, status, worker_type)
    response = HttpResponse(content_type='text/csv')
    cd = 'attachment; filename=%s_contacts.csv' % str(event).replace(' ', '_')
    response['Content-Disposition'] = cd
    writer = csv.writer(response)
    writer.writerow(['Name', 'email'])
    for row in data:
        writer.writerow(row)
    return response


def contact_performers(conference=None):
    if not conference:
        conference = get_current_conference()
    from gbe.models import Act
    contacts = [act.actitem_ptr for act in Act.objects.filter(
        conference=conference)]
    header = ['Act',
              'Performer',
              'Profile',
              'email',
              'Phone',
              'status',
              'Show(s)',
              'Rehearsal(s)']
    contact_info = []
    for c in contacts:
        act = c.as_subtype
        performer = act.performer
        contact_info.append(
            [act.title,
             str(performer),
             str(performer.contact),
             act.contact_email,
             act.performer.contact.phone,
             act.accepted,
             ",".join(map(str, act.get_scheduled_shows())),
             ",".join(map(str, act.get_scheduled_rehearsals()))]
        )
    return header, contact_info


def contact_volunteers(conference=None):
    header = ['Name',
              'Phone',
              'Email',
              'Volunteer Category',
              'Volunteer Role',
              'Event']
    volunteer_categories = dict(volunteer_interests_options)
    if not conference:
        conference = get_current_conference()
    from gbe.models import Volunteer
    contacts = filter(lambda worker: worker.allocations.count() > 0,
                      [vol.profile.workeritem_ptr.worker_set.first() for vol in
                       Volunteer.objects.filter(conference=conference)
                       if vol.profile.workeritem_ptr.worker_set.exists()])

    volunteers = Volunteer.objects.filter(conference=conference).annotate(
        Count('profile__workeritem_ptr__worker')).order_by(
            '-profile__workeritem_ptr__worker__count')

    contact_info = []
    for v in volunteers:
        profile = v.profile
        for worker in profile.workeritem_ptr.worker_set.all():
            for allocation in worker.allocations.all():
                try:
                    container = allocation.event.container_event
                    parent_event = container.parent_event
                except:
                    parent_event = allocation.event
                contact_info.append(
                    [profile.display_name,
                     profile.phone,
                     profile.contact_email,
                     volunteer_categories.get(
                         allocation.event.as_subtype.volunteer_category, ''),
                     str(allocation.event),
                     str(parent_event)])
        else:
            interests = eval(v.interests)
            contact_info.append([profile.display_name,
                                 profile.phone,
                                 profile.contact_email,
                                 ','.join([volunteer_categories[i]
                                           for i in interests]),
                                 'Application',
                                 'Application']
                                )
    return header, contact_info


def contact_teachers(conference=None):
    if not conference:
        conference = get_current_conference()

    header = ['email',
              'Class',
              'Role',
              'Performer Name',
              'Display Name',
              'Phone']
    from gbe.models import Class
    classes = Class.objects.filter(conference=conference)
    contact_info = []

    for c in classes:
        for se in c.scheduler_events.all():
            contact_info += se.class_contacts2()

        contact_info.append(
            [c.teacher.contact_email,
             c.title.encode('utf-8').strip(),
             'Bidder',
             c.teacher.name.encode('utf-8').strip(),
             c.teacher.contact.display_name.encode('utf-8').strip(),
             c.teacher.contact.phone]
        )
    return header, contact_info


def contact_vendors(conference=None):
    from gbe.models import Vendor
    acceptance_dict = dict(acceptance_states)
    contacts = Vendor.objects.filter(conference=conference)
    header = ['Business Name', 'Personal Name', 'Email', 'Status']
    contact_info = [[v.title,
                     v.profile.display_name,
                     v.profile.contact_email,
                     acceptance_dict[v.accepted]] for v in contacts]
    return header, contact_info


def contact_by_role(request, participant_type):
    validate_perms(request, "any", require=True)
    conference = get_current_conference()
    if participant_type == 'Teachers':
        header, contact_info = contact_teachers(conference)
    elif participant_type == 'Performers':
        header, contact_info = contact_performers(conference)
    elif participant_type == 'Volunteers':
        header, contact_info = contact_volunteers(conference)
    elif participant_type == 'Vendors':
        header, contact_info = contact_vendors(conference)
    else:
        header = []
        contact_info = []
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename=%s_contacts.csv' % participant_type
    writer = csv.writer(response)
    writer.writerow(header)
    for row in contact_info:
        writer.writerow(row)
    return response


@login_required
def add_event(request, eventitem_id, event_type='Class'):
    '''
    Add an item to the conference schedule and/or set its schedule details
    (start time, location, duration, or allocations)
    Takes a scheduler.EventItem id - BB - separating new event from editing
    existing, so that edit can identify particular schedule items, while this
    identifies the event item.
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))

    eventitem = get_object_or_404(EventItem, eventitem_id=eventitem_id)
    item = eventitem.child()
    template = 'scheduler/event_schedule.tmpl'
    eventitem_view = get_event_display_info(eventitem_id)

    if request.method == 'POST':
        event_form = EventScheduleForm(request.POST,
                                       prefix='event')

        if (event_form.is_valid() and True):
            s_event = event_form.save(commit=False)
            s_event.eventitem = item
            data = event_form.cleaned_data

            if data['duration']:
                s_event.set_duration(data['duration'])

            l = LocationItem.objects.get_subclass(room__name=data['location'])
            s_event.save()
            s_event.set_location(l)
            if data['teacher']:
                s_event.unallocate_role('Teacher')
                s_event.allocate_worker(data['teacher'].workeritem, 'Teacher')
            s_event.save()
            if data['moderator']:
                s_event.unallocate_role('Moderator')
                s_event.allocate_worker(data['moderator'].workeritem,
                                        'Moderator')
            if len(data['panelists']) > 0:
                s_event.unallocate_role('Panelist')
                for panelist in data['panelists']:
                    s_event.allocate_worker(panelist.workeritem, 'Panelist')

            if data['staff_lead']:
                s_event.unallocate_role('Staff Lead')
                s_event.allocate_worker(data['staff_lead'].workeritem,
                                        'Staff Lead')

            if data['description'] or data['title']:
                c_event = s_event.as_subtype
                c_event.description = data['description']
                c_event.title = data['title']
                c_event.save()

            return HttpResponseRedirect(reverse('event_schedule',
                                                urlconf='scheduler.urls',
                                                args=[event_type]))
        else:
            return render(request, template, {'eventitem': eventitem_view,
                                              'form': event_form,
                                              'user_id': request.user.id,
                                              'event_type': event_type})
    else:
        initial_form_info = {'duration': item.duration,
                             'description': item.sched_payload['description'],
                             'title': item.sched_payload['title']}
        if item.__class__.__name__ == 'Class':
            initial_form_info['teacher'] = item.teacher
            initial_form_info['duration'] = Duration(item.duration.days,
                                                     item.duration.seconds)

        form = EventScheduleForm(prefix='event',
                                 initial=initial_form_info)

    return render(request, template, {'eventitem': eventitem_view,
                                      'form': form,
                                      'user_id': request.user.id,
                                      'event_type': event_type})


@login_required
def edit_event(request, scheduler_event_id, event_type='class'):
    '''
    Add an item to the conference schedule and/or set its schedule details
    (start time, location, duration, or allocations)
    Takes a scheduler.Event id
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))

    item = get_object_or_404(Event, id=scheduler_event_id)

    if request.method == 'POST':
        event_form = EventScheduleForm(request.POST,
                                       instance=item,
                                       prefix='event')
        if event_form.is_valid():
            s_event = event_form.save(commit=False)
            data = event_form.cleaned_data

            if data['duration']:
                s_event.set_duration(data['duration'])
            l = LocationItem.objects.get_subclass(
                room__name=data['location'])
            s_event.save()
            s_event.set_location(l)

            s_event.unallocate_role('Teacher')
            if data['teacher']:
                s_event.allocate_worker(data['teacher'].workeritem, 'Teacher')
            s_event.save()

            s_event.unallocate_role('Moderator')
            if data['moderator']:
                s_event.allocate_worker(data['moderator'].workeritem,
                                        'Moderator')

            s_event.unallocate_role('Panelist')
            if len(data['panelists']) > 0:
                for panelist in data['panelists']:
                    s_event.allocate_worker(panelist.workeritem, 'Panelist')

            s_event.unallocate_role('Staff Lead')
            if data['staff_lead']:
                s_event.allocate_worker(data['staff_lead'].workeritem,
                                        'Staff Lead')

            if data['description'] or data['title']:
                c_event = s_event.as_subtype
                c_event.description = data['description']
                c_event.title = data['title']
                c_event.save()
            return HttpResponseRedirect(reverse('edit_event',
                                                urlconf='scheduler.urls',
                                                args=[event_type,
                                                      scheduler_event_id]))
        else:
            template = 'scheduler/event_schedule.tmpl'
            return render(request, template, {
                'eventitem': get_event_display_info(
                    item.eventitem.eventitem_id),
                'form': event_form,
                'event_type': item.event_type_name})

    else:
        return edit_event_display(request, item)


def edit_event_display(request, item, errorcontext=None):
    from gbe.models import Performer

    template = 'scheduler/event_schedule.tmpl'
    context = {'user_id': request.user.id,
               'event_id': item.id,
               'event_edit_url': reverse('edit_event',
                                         urlconf='scheduler.urls',
                                         args=[item.event_type_name,
                                               item.id])}
    context['eventitem'] = get_event_display_info(item.eventitem.eventitem_id)

    initial = {}
    initial['duration'] = item.duration
    initial['day'] = get_conference_day(
        conference=item.eventitem.get_conference(),
        date=item.starttime.date())
    initial['time'] = item.starttime.strftime("%H:%M:%S")
    initial['description'] = item.as_subtype.sched_payload['description']
    initial['title'] = item.as_subtype.sched_payload['title']
    initial['location'] = item.location

    allocs = ResourceAllocation.objects.filter(event=item)
    workers = [Worker.objects.get(id=a.resource.id)
               for a in allocs if type(a.resource.item) == WorkerItem]
    teachers = [worker for worker in workers if worker.role == 'Teacher']
    moderators = [worker for worker in workers if worker.role == 'Moderator']
    panelists = Performer.objects.filter(worker__role='Panelist',
                                         worker__allocations__event=item)
    staff_leads = [worker for worker in workers if worker.role == 'Staff Lead']

    # Set initial values for specialized event roles
    if len(teachers) > 0:
        initial['teacher'] = teachers[0].item

    elif item.event_type_name == 'Class':
        try:
            initial['teacher'] = item.as_subtype.teacher
        except:
            pass

    if len(moderators) > 0:
        initial['moderator'] = moderators[0].item
    if len(panelists) > 0:
        initial['panelists'] = panelists
    if len(staff_leads) > 0:
        initial['staff_lead'] = staff_leads[0].item

    context['event_type'] = item.event_type_name

    if validate_perms(request, ('Volunteer Coordinator',), require=False):
        if (item.event_type_name == 'GenericEvent' and
                item.as_subtype.type == 'Volunteer'):

            context.update(get_worker_allocation_forms(item, errorcontext))
            context.update(show_potential_workers(item))
        else:
            context.update(get_manage_opportunity_forms(item,
                                                        initial,
                                                        errorcontext))

    context['form'] = EventScheduleForm(
        prefix='event',
        instance=item,
        initial=initial)
    return render(request, template, context)


def view_list(request, event_type='All'):
    if not event_type.lower() in list_titles:
        event_type = "All"

    current_conf = get_current_conference()
    conf_slug = request.GET.get('conference', None)
    if not conf_slug:
        conference = current_conf
    else:
        conference = get_conference_by_slug(conf_slug)
    items = get_events_list_by_type(event_type, conference)
    events = [
        {'eventitem': item,
         'scheduled_events': item.scheduler_events.order_by('starttime'),
         'detail': reverse('detail_view',
                           urlconf='scheduler.urls',
                           args=[item.eventitem_id])
         }
        for item in items]

    conferences = conference_list()
    return render(request, 'scheduler/event_display_list.tmpl',
                  {'title': list_titles.get(event_type.lower(), ""),
                   'view_header_text': list_text.get(event_type.lower(), ""),
                   'labels': event_labels,
                   'events': events,
                   'conferences': conferences,
                   'etype': event_type,
                   })


def calendar_view(request=None,
                  event_type='Show',
                  day=None,
                  time_format=None,
                  duration=Duration(minutes=60)):
    conf_slug = request.GET.get('conf', None)
    if conf_slug:
        conf = get_conference_by_slug(conf_slug)
    else:
        conf = get_current_conference()

    cal_times = cal_times_for_conf(conf, day)

    if event_type == 'All':
        event_types = ['Show',
                       'Class',
                       'Special Event',
                       'Master Class',
                       'Drop-In Class']
        events = []
        for e_type in event_types:
            events = events + event_info(confitem_type=e_type,
                                         cal_times=cal_times,
                                         conference=conf)
    elif event_type == 'Show':
        events = event_info(confitem_type='Show',
                            cal_times=cal_times,
                            conference=conf)
        events += event_info(confitem_type='Special Event',
                             cal_times=cal_times,
                             conference=conf)
        events += event_info(confitem_type='Master Class',
                             cal_times=cal_times,
                             conference=conf)
        events += event_info(confitem_type='Drop-In Class',
                             cal_times=cal_times,
                             conference=conf)
    else:
        events = event_info(confitem_type=event_type, cal_times=cal_times,
                            conference=conf)
    events = overlap_clear(events)
    if time_format is None:
        time_format = set_time_format()

    # Changing function to get table labels from the request
    table = {}
    table['rows'] = table_prep(events,
                               duration,
                               cal_start=cal_times[0],
                               cal_stop=cal_times[1])
    table['name'] = 'Event Calendar for the Great Burlesque Expo of 2015'
    table['link'] = 'http://burlesque-expo.com'
    table['x_name'] = {}
    table['x_name']['html'] = 'Rooms'
    table['x_name']['link'] = 'http://burlesque-expo.com/class_rooms'
    # TO DO: Get rid of hard-coded links

    template = 'scheduler/Sched_Display.tmpl'

    return render(request, template, table)
