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
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from scheduler.models import *
from scheduler.forms import *
from gbe.scheduling.forms import (
    VolunteerOpportunityForm,
    WorkerAllocationForm,
)
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
    event_info,
    overlap_clear,
    table_prep,
)
from scheduler.views.functions import (
    get_event_display_info,
    get_events_display_info,
)
from gbe.functions import (
    conference_slugs,
    eligible_volunteers,
    get_current_conference,
    get_conference_by_slug,
    get_conference_day,
    get_events_list_by_type,
    validate_perms,
    validate_profile,
)
from gbe.views.class_display_functions import get_scheduling_info
from django.contrib import messages
from expo.settings import DATE_FORMAT
from django.utils.formats import date_format


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
                                         urlconf='gbe.scheduling.urls',
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
        details['title'] = act.b_title
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
    new_forms = []
    for details, alloc in forms:
        new_forms.append((
            ActScheduleForm(initial=details,
                            prefix='allocation_%d' % alloc.id),
            details['performer'].contact.user_object.is_active))

    template = 'scheduler/act_schedule.tmpl'
    return render(request,
                  template,
                  {'forms': new_forms})


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
    writer.writerow(['Name', 'Email', 'Phone', 'Role/Accepted', 'Title'])
    for row in data:
        writer.writerow(row)
    return response


def contact_performers(conference):
    if not conference:
        conference = get_current_conference()
    from gbe.models import Act
    contacts = [act.actitem_ptr for act in Act.objects.filter(
        b_conference=conference,
        performer__contact__user_object__is_active=True)]
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
            [act.b_title,
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

    volunteers = Volunteer.objects.filter(
        b_conference=conference,
        profile__user_object__is_active=True).annotate(
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
    classes = Class.objects.filter(
        b_conference=conference)
    contact_info = []

    for c in classes:
        for se in c.scheduler_events.all():
            contact_info += se.class_contacts2()

        if c.teacher.contact.user_object.is_active:
            contact_info.append(
                [c.teacher.contact_email,
                 c.b_title.encode('utf-8').strip(),
                 'Bidder',
                 c.teacher.name.encode('utf-8').strip(),
                 c.teacher.contact.display_name.encode('utf-8').strip(),
                 c.teacher.contact.phone]
            )
    return header, contact_info


def contact_vendors(conference):
    from gbe.models import Vendor
    acceptance_dict = dict(acceptance_states)
    contacts = Vendor.objects.filter(
        b_conference=conference,
        profile__user_object__is_active=True)
    header = ['Business Name', 'Personal Name', 'Email', 'Status']
    contact_info = [[v.b_title,
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


def edit_event_display(request, item, errorcontext=None):
    from gbe.models import Performer

    template = 'gbe/scheduling/event_schedule.tmpl'
    context = {'user_id': request.user.id,
               'event_id': item.id,
               'event_edit_url': reverse('edit_event_schedule',
                                         urlconf='gbe.scheduling.urls',
                                         args=[item.event_type_name,
                                               item.eventitem.eventitem_id,
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

            context.update(get_volunteer_info(item))

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

    return render(request, 'scheduler/event_display_list.tmpl',
                  {'title': list_titles.get(event_type.lower(), ""),
                   'view_header_text': list_text.get(event_type.lower(), ""),
                   'labels': event_labels,
                   'events': events,
                   'conference_slugs': conference_slugs(),
                   'etype': event_type,
                   'conf_slug': conf_slug,
                   })


def calendar_view(request=None,
                  event_type='Show',
                  day=None,
                  duration=Duration(minutes=30)):
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
        if day:
            table['day'] = "%s - %s" % (
                day,
                date_format(cal_times[0], "DATE_FORMAT"))
        else:
            table['day'] = "%s - %s" % (
                date_format(cal_times[0], "DATE_FORMAT"),
                date_format(cal_times[1], "DATE_FORMAT"))
        table['name'] = 'Event Calendar for the Great Burlesque Expo'
        table['link'] = 'http://burlesque-expo.com'
        table['x_name'] = {}
        table['x_name']['html'] = 'Rooms'
        table['x_name']['link'] = 'http://burlesque-expo.com/class_rooms'
    # TO DO: Get rid of hard-coded links

    template = 'scheduler/sched_display.tmpl'

    return render(request, template, table)
