from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.formats import date_format
from scheduler.models import EventItem


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
                                           e_conference=conference)
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
                                       urlconf='gbe.scheduling.urls',
                                       args=[entry['eventitem'].eventitem_id])}

        if entry['schedule_event']:
            eventinfo['edit'] = reverse('edit_event_schedule',
                                        urlconf='gbe.scheduling.urls',
                                        args=[event_type,
                                              entry['eventitem'].eventitem_id,
                                              entry['schedule_event'].id])
            eventinfo['location'] = entry['schedule_event'].location
            eventinfo['datetime'] = date_format(
                entry['schedule_event'].starttime, "DATETIME_FORMAT")
            eventinfo['max_volunteer'] = entry['schedule_event'].max_volunteer
            eventinfo['volunteer_count'] = entry[
                'schedule_event'].volunteer_count
            eventinfo['delete'] = reverse('delete_occurrence',
                                          urlconf='gbe.scheduling.urls',
                                          args=[entry['schedule_event'].id])

        else:
            eventinfo['create'] = reverse(
                'create_event_schedule',
                urlconf='gbe.scheduling.urls',
                args=[event_type,
                      entry['eventitem'].eventitem_id])
            eventinfo['location'] = entry['confitem'].default_location
            eventinfo['datetime'] = None
            eventinfo['max_volunteer'] = None
        eventslist.append(eventinfo)
    return eventslist
