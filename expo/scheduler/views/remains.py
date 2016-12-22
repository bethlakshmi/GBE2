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
from django.conf import settings
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
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from datetime import datetime
from datetime import time as dttime
import pytz
import csv
from scheduler.table import table
from gbe_forms_text import (
    list_titles,
)
from gbetext import acceptance_states
from gbe.duration import (
    Duration,
    DateTimeRange,
)
from scheduler.functions import (
    cal_times_for_conf,
    conference_dates,
    event_info,
    overlap_clear,
    table_prep,
)
from scheduler.views.functions import (
    get_event_display_info,
    get_events_display_info,
    set_single_role,
    set_multi_role,
)
from gbe.functions import (
    conference_list,
    eligible_volunteers,
    get_current_conference,
    get_conference_by_slug,
    get_conference_day,
    get_events_list_by_type,
    send_schedule_update_mail,
    validate_perms,
    validate_profile,
)
from gbe.views.class_display_functions import get_scheduling_info
from django.contrib import messages


@login_required
@never_cache
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


@login_required
@never_cache
def schedule_acts(request, show_id=None):
    '''
    Display a list of acts available for scheduling, allows setting show/order
    '''
    validate_perms(request, ('Scheduling Mavens',))

    import gbe.models as conf

    # came from the schedule selector
    if request.method == "POST":
        show_id = request.POST.get('show_id', 'POST')

    # no show selected yet
    if show_id is None or show_id.strip() == '':
        template = 'scheduler/select_event_type.tmpl'
        show_options = EventItem.objects.all().select_subclasses()
        show_options = filter(
            lambda event: (
                type(event) == conf.Show) and (
                event.get_conference().status != 'completed'), show_options)
        return render(request, template, {'show_options': show_options})

    # came from an ActSchedulerForm
    if show_id == 'POST':
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
            try:
                ordering = alloc.ordering
                ordering.order = data['order']
            except:
                ordering = Ordering(allocation=alloc, order=data['order'])
            ordering.save()

        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    # get allocations involving the show we want
    show = get_object_or_404(conf.Show, pk=show_id)
    event = show.scheduler_events.first()

    allocations = ResourceAllocation.objects.filter(event=event)
    allocations = [a for a in allocations if type(a.resource.item) == ActItem]

    forms = []
    for alloc in allocations:
        actitem = alloc.resource.item
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

        forms.append([details, alloc])
    forms = sorted(forms, key=lambda f: f[0]['order'])
    forms = [ActScheduleForm(initial=details,
                             prefix='allocation_%d' % alloc.id)
             for (details, alloc) in forms]

    template = 'scheduler/act_schedule.tmpl'
    return render(request,
                  template,
                  {'forms': forms})


@login_required
def delete_schedule(request, scheduler_event_id):
    '''
    Remove the scheduled item
    '''
    validate_perms(request, ('Scheduling Mavens',))
    event = get_object_or_404(Event, id=scheduler_event_id)
    type = event.event_type_name
    event.delete()
    return HttpResponseRedirect(reverse('event_schedule',
                                        urlconf='scheduler.urls',
                                        args=[type]))


@login_required
def delete_event(request, eventitem_id, event_type):
    '''
    Remove any scheduled items, make basic event item invisible
    '''
    validate_perms(request, ('Scheduling Mavens',))
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
                'worker_alloc_forms' in errorcontext and
                errorcontext['worker_alloc_forms'].cleaned_data[
                    'alloc_id'] == alloc.id):
            forms.append(errorcontext['worker_alloc_forms'])
        else:
            forms.append(WorkerAllocationForm(
                initial={'worker': alloc.resource.item.as_subtype,
                         'role': Worker.objects.get(
                             id=alloc.resource.id).role,
                         'label': alloc.get_label,
                         'alloc_id': alloc.id}))
    if errorcontext and 'new_worker_alloc_form' in errorcontext:
        forms.append(errorcontext['new_worker_alloc_form'])
    else:
        forms.append(WorkerAllocationForm(initial={'role': 'Volunteer',
                                                   'alloc_id': -1}))
    return {'worker_alloc_forms': forms,
            'worker_alloc_headers': ['Worker', 'Role', 'Notes'],
            'opp_id': opp.id}


@login_required
@never_cache
def allocate_workers(request, opp_id):
    '''
    Process a worker allocation form
    Needs a scheduler_event id
    '''
    if request.method != "POST":
        raise Http404

    coordinator = validate_perms(request, ('Volunteer Coordinator',))

    opp = get_object_or_404(Event, id=opp_id)
    form = WorkerAllocationForm(request.POST)

    if 'delete' in request.POST.keys():
        alloc = ResourceAllocation.objects.get(id=request.POST['alloc_id'])
        res = alloc.resource
        profile = res.as_subtype.workeritem
        alloc.delete()
        res.delete()
        # This delete looks dangerous, considering that Event.allocate_worker
        # seems to allow us to create multiple allocations for the same Worker
        send_schedule_update_mail("Volunteer", profile)

    elif not form.is_valid():
        if request.POST['alloc_id'] == '-1':
            form.data['alloc_id'] = -1
            return edit_event_display(
                request,
                opp,
                {'new_worker_alloc_form': form})
        else:
            get_object_or_404(ResourceAllocation,
                              id=request.POST['alloc_id'])
            return edit_event_display(
                request,
                opp,
                {'worker_alloc_forms': form})

    else:
        data = form.cleaned_data
        if data.get('worker', None):
            if data['role'] == "Volunteer":
                data['worker'].workeritem.as_subtype.check_vol_bid(
                    opp.eventitem.get_conference())
            warnings = opp.allocate_worker(
                data['worker'].workeritem,
                data['role'],
                data['label'],
                data['alloc_id'])
            for warning in warnings:
                messages.warning(
                    request,
                    warning)
            send_schedule_update_mail("Volunteer", data['worker'])
    return HttpResponseRedirect(reverse('edit_event',
                                        urlconf='scheduler.urls',
                                        args=[opp.event_type_name, opp_id]))


@login_required
@never_cache
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


@login_required
@never_cache
def contact_info(request,
                 event_id,
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
    event = get_object_or_404(Event, schedulable_ptr_id=event_id)
    data = event.contact_info(resource_type, status, worker_type)
    response = HttpResponse(content_type='text/csv')
    cd = 'attachment; filename=%s_contacts.csv' % str(event).replace(' ', '_')
    response['Content-Disposition'] = cd
    writer = csv.writer(response)
    writer.writerow(['Name', 'email'])
    for row in data:
        writer.writerow(row)
    return response


def contact_performers(conference):
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


def contact_volunteers(conference):
    header = ['Name',
              'Phone',
              'Email',
              'Volunteer Category',
              'Volunteer Role',
              'Event']
    from gbe.models import Volunteer

    volunteers = Volunteer.objects.filter(conference=conference).annotate(
        Count('profile__workeritem_ptr__worker')).order_by(
            '-profile__workeritem_ptr__worker__count')
    contact_info = []
    for v in volunteers:
        profile = v.profile
        for worker in profile.workeritem_ptr.worker_set.all().filter(
                role="Volunteer"):
            allocation_events = (
                a.event for a in worker.allocations.all()
                if a.event.eventitem.get_conference() == conference)
            for event in allocation_events:
                try:
                    parent_event = event.container_event.parent_event
                except:
                    parent_event = event
                try:
                    interest = event.as_subtype.volunteer_type.interest
                except:
                    interest = ''

                contact_info.append(
                    [profile.display_name,
                     profile.phone,
                     profile.contact_email,
                     interest,
                     str(event),
                     str(parent_event)])
        else:
            contact_info.append(
                [profile.display_name,
                 profile.phone,
                 profile.contact_email,
                 ','.join([
                    i.interest.interest
                    for i in v.volunteerinterest_set.all().filter(
                        interest__visible=True,
                        rank__gt=3).order_by(
                        'interest__interest')]),
                 'Application',
                 'Application']
            )
    return header, contact_info


def contact_teachers(conference):
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


def contact_vendors(conference):
    from gbe.models import Vendor
    acceptance_dict = dict(acceptance_states)
    contacts = Vendor.objects.filter(conference=conference)
    header = ['Business Name', 'Personal Name', 'Email', 'Status']
    contact_info = [[v.title,
                     v.profile.display_name,
                     v.profile.contact_email,
                     acceptance_dict[v.accepted]] for v in contacts]
    return header, contact_info


@login_required
@never_cache
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
@never_cache
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
            set_single_role(s_event, data)
            set_multi_role(s_event, data)
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


def get_volunteer_info(opp, errorcontext=None):
    volunteer_set = []
    for volunteer in eligible_volunteers(
            opp.start_time,
            opp.end_time,
            opp.eventitem.get_conference()):
        assign_form = WorkerAllocationForm(
            initial={'role': 'Volunteer',
                     'worker': volunteer.profile,
                     'alloc_id': -1})
        assign_form.fields['worker'].widget = forms.HiddenInput()
        assign_form.fields['label'].widget = forms.HiddenInput()
        volunteer_set += [{
            'display_name': volunteer.profile.display_name,
            'interest': rank_interest_options[
                volunteer.volunteerinterest_set.get(
                    interest=opp.as_subtype.volunteer_type).rank],
            'available': volunteer.check_available(
                opp.start_time,
                opp.end_time),
            'conflicts': volunteer.profile.get_conflicts(opp),
            'id': volunteer.pk,
            'assign_form': assign_form
        }]

    return {'eligible_volunteers': volunteer_set}


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
            context.update(get_volunteer_info(item))
        else:
            context.update(get_manage_opportunity_forms(item,
                                                        initial,
                                                        errorcontext))
    scheduling_info = get_scheduling_info(item.as_subtype)
    if scheduling_info:
        context['scheduling_info'] = scheduling_info

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
        events = event_info(confitem_type=event_type,
                            cal_times=cal_times,
                            conference=conf)

    events = overlap_clear(events)

    table = {}

    if len(events) > 0:
        # Changing function to get table labels from the request
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

    template = 'scheduler/sched_display.tmpl'

    return render(request, template, table)
