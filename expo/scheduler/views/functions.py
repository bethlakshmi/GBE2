from django.core.urlresolvers import reverse
from django.http import Http404

from scheduler.models import EventItem
from gbetext import event_labels


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


def get_events_display_info(event_type='Class'):
    '''
    Helper for displaying lists of events. Gets a supply of conference event
    items and munges them into displayable shape
    "Conference event items" = things in the conference model which extend
    EventItems and therefore
    could be Events
    '''
    import gbe.models as gbe
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
                "DATETIME_FORMAT")
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
            eventinfo['location'] = entry['confitem'].default_location
            eventinfo['datetime'] = None
            eventinfo['max_volunteer'] = None
        eventslist.append(eventinfo)
    return eventslist


def set_single_role(event, data, roles=None):
    if not roles:
        roles = [('teacher', 'Teacher'),
                 ('moderator', 'Moderator'),
                 ('staff_lead', 'Staff Lead')]
    for role_key, role in roles:
        event.unallocate_role(role)
        if data[role_key]:
            event.allocate_worker(data[role_key].workeritem, role)
    event.save()


def set_multi_role(event, data, roles=None):
    if not roles:
        roles = [('panelists', 'Panelist')]
    for role_key, role in roles:
        event.unallocate_role(role)
        if len(data[role_key]) > 0:
            for worker in data[role_key]:
                event.allocate_worker(worker.workeritem, role)
    event.save()
