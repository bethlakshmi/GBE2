from table import table
from datetime import (
    date,
    timedelta,
    time,
    datetime
)
from calendar import timegm
from gbe.duration import (
    Duration,
    DateTimeRange,
    timedelta_to_duration,
)
from random import choice

import math
from expo.settings import (
    DATETIME_FORMAT,
    TIME_FORMAT,
    DAY_FORMAT,
)
from django.utils.formats import date_format

from django.core.urlresolvers import reverse
import pytz

conference_days = (
    (date_format(datetime(2015, 02, 19), "DAY_FORMAT"), 'Thursday'),
    (date_format(datetime(2015, 02, 20), "DAY_FORMAT"), 'Friday'),
    (date_format(datetime(2015, 02, 21), "DAY_FORMAT"), 'Saturday'),
    (date_format(datetime(2015, 02, 22), "DAY_FORMAT"), 'Sunday'),
)

utc = pytz.timezone('UTC')

conference_datetimes = (
    datetime(2015, 02, 19, tzinfo=utc),
    datetime(2015, 02, 20, tzinfo=utc),
    datetime(2015, 02, 21, tzinfo=utc),
    datetime(2015, 02, 22, tzinfo=utc),
)

time_start = 8 * 60
time_stop = 24 * 60

conference_times = [(time(mins / 60, mins % 60),
                     date_format(time(mins / 60, mins % 60), \
                                 "TIME_FORMAT"))
                    for mins in range(time_start, time_stop, 30)]

conference_dates = {"Thursday": "2015-02-19",
                    "Friday": "2015-02-20",
                    "Saturday": "2015-02-21",
                    "Sunday": "2015-02-22"}

hour = Duration(seconds=3600)

monday = datetime(2015, 2, 23)


def init_time_blocks(events,
                     block_size,
                     time_format = "DATETIME_FORMAT",
                     cal_start=None,
                     cal_stop=None,
                     trim_to_block_size=True,
                     offset=None,
                     strip_empty_blocks='both'):
    '''
    Find earliest start time and latest stop time and generate a list of
    schedule blocks enclosing these.
    trim_to_block_size  ensures that the starting block starts on an integer
    multiple of block_size
    offset: not implemented. Will allow setting an offset for schedule blocks
    cal_start and cal_stop are preset values for start time and stop time,
    as datetime objects
    (will allow for time objects, but not yet)
    If provided, they are assumed to be correct. (ie, we don't adjust them,
    just use them)
    strip_empty_blocks allows us to specify whether empty blocks will
    be removed from the start or end of the calendar, or both. Valuea
    in ("start", "stop", "both") do the right things.
    '''

    if not cal_start:
        cal_start = sorted([event['start_time'] for event in events])[0]
    elif isinstance(cal_start, time):
        cal_start = datetime.combine(datetime.min, cal_start)

    if not cal_stop:
        cal_stop = sorted([event['stop_time'] for event in events])[-1]
    elif isinstance(cal_stop, time):
        cal_stop = datetime.combine(datetime.min, cal_stop)

    if cal_stop < cal_start:    # assume that we've gone past midnight
        cal_stop += timedelta(days=1)
    if trim_to_block_size:
        pass  # TO DO

    events = [event for event in events
              if event['stop_time'] > cal_start and
              event['start_time'] < cal_stop]
    events = sorted(events, key=lambda event: event['start_time'])
    if not events:
        return [], cal_start, cal_stop
    if strip_empty_blocks in ('both', 'start'):
        cal_start = max(cal_start, events[0]['start_time'])
    events = sorted(events, key=lambda event: event['stop_time'])
    if strip_empty_blocks in ('both', 'stop'):
        cal_stop = min(cal_stop, events[-1]['stop_time'])
    schedule_duration = timedelta_to_duration(cal_stop-cal_start)
    blocks_count = int(math.ceil(schedule_duration/block_size))
    block_labels = [date_format((cal_start + block_size * b), \
                                time_format)
                    for b in range(blocks_count)]
    return block_labels, cal_start, cal_stop


def init_column_heads(events):
    '''
    Scan events and return list of room names.
    '''
    return sorted(list(set([e['location'] for e in events])))


def normalize(event, schedule_start, schedule_stop, block_labels, block_size):
    '''
    Set a startblock and rowspan for event such that startblock is the
    earliest block containing the event's start time, and rowspan is the number
    of blocks it occupies block_size should be a Duration
    '''

    if event['start_time'] < schedule_start:
        relative_start = Duration(seconds=0)
    else:
        relative_start = event['start_time'] - schedule_start
    if event['stop_time'] > schedule_stop:
        working_stop_time = timedelta_to_duration(
            schedule_stop - schedule_start)
    else:
        working_stop_time = timedelta_to_duration(
            event['stop_time'] - schedule_start)
    event['startblock'] = timedelta_to_duration(relative_start) // block_size
    event['startlabel'] = block_labels[event['startblock']]
    event['rowspan'] = int(
        math.ceil(working_stop_time / block_size))-event['startblock']


def overlap_check(events):
    '''
    Return a list of event tuples such that all members of a
    tuple are in the same room and stop time of one event overlaps
    with at least one other member of the tuple
    '''
    overlaps = []
    for location in set([e['location'] for e in events]):
        conflict_set = []
        location_events = sorted(
            [event for event in events if event['location'] == location],
            key=lambda event: event['start_time'])
        prev_stop = location_events[0]['stop_time']
        prev_event = location_events[0]
        for event in location_events[1:]:
            if event['start_time'] < prev_stop:
                conflict_set.append((prev_event, event))
            else:
                if len(conflict_set) > 0:
                    overlaps += conflict_set
                    conflict_set = []
            prev_stop = event['stop_time']
            prev_event = event
        if len(conflict_set) > 0:
            overlaps += conflict_set
            conflict_set = []
    return overlaps


def overlap_clear(events):
    '''
    Return a list of event tuples such that all members of a tuple are in
    the same room and stop time of one event overlaps with at least one
    other member of the tuple
    '''
    from gbetext import overlap_location_text
    for location in set([e['location'] for e in events]):
        location_events = sorted(
            [event for event in events if event['location'] == location],
            key=lambda event: event['start_time'])
        prev_stop = location_events[0]['stop_time']
        prev_event = location_events[0]
        for event in location_events[1:]:
            if event['start_time'] < prev_stop:
                if event['location'] == prev_event['location']:
                    event['location'] = event['location']+overlap_location_text
            prev_stop = event['stop_time']
            prev_event = event
    return events

# default handling of overlapping events:
# public calendars: do not show any overlapping events
# Second pass: display in calendar with fancy trickery. (handwave, handwave)
# admin calendars: combine overlapping events into "OVERLAP" event
# possibly also offer calendar showing only overlaps


def add_to_table(event, table, block_labels):
    '''
    Insert event into appropriate cell in table
    If event occupies multiple blocks, insert "placeholder" in
    subsequent table cells (nonbreaking space)
    '''
    table[event['location'],
          block_labels[event['startblock']]
          ] = '<td rowspan=%d class=\'%s\'>%s</td>' % (
        event['rowspan'], " ".join([event.get('css_class', ''),
                                    event['location'].replace(' ', '_'),
                                    event['type']]),
        event.get('html', 'FOO'))
    for i in range(1, event['rowspan']):
        table[event['location'],
              block_labels[event['startblock']+i]
              ] = '&nbsp;'


def html_prep(event):
    '''
    If an event object does not have a HTML table block set up, this will
    generate one.
    '''
    if 'html' in event.keys():
        return
    html = '<li><a href=\'%s\'>%s</a></li>' % (event['link'], event['title'])
    if 'short_desc' in event.keys():
        #  short_desc is a short description, which is optional
        html = html+event['short_desc']
    event['html'] = html


def html_headers(table, headerStart='<TH>', headerEnd='</TH>'):
    '''
    Checks the header positions for a table, rendered as a list of lists,
    for HTML tags, and adds '<TH>' + cell + '</TH>' if they are absent.
    '''
    for cell in range(len(table[0])):
        if not table[0][cell].startswith(headerStart):
            table[0][cell] = headerStart + table[0][cell]
        if not table[0][cell].endswith(headerEnd):
            table[0][cell] = table[0][cell] + headerEnd

    for cell in range(1, len(table)):
        if not table[cell][0].startswith(headerStart):
            table[cell][0] = headerStart + table[cell][0]
        if not table[cell][0].endswith(headerEnd):
            table[cell][0] = table[cell][0] + headerEnd
    return table


def table_prep(events,
               block_size,
               time_format=DATETIME_FORMAT,
               cal_start=None,
               cal_stop=None,
               col_heads=None):
    '''
    Generate a calendar table based on submitted events
    '''
    block_labels, cal_start, cal_stop = init_time_blocks(events,
                                                         block_size,
                                                         time_format,
                                                         cal_start,
                                                         cal_stop)
    events = filter(lambda e: ((cal_start <= e['start_time'] < cal_stop)) or
                    ((cal_start < e['stop_time'] <= cal_stop)), events)

    if not col_heads:
        col_heads = init_column_heads(events)
    cal_table = table(rows=block_labels,
                      columns=col_heads,
                      default='<td></td>')

    for event in events:
        normalize(event, cal_start, cal_stop, block_labels, block_size)
        html_prep(event)

    # overlaps = overlap_check(events)
    # don't worry about handling now,
    # but write overlap handlers and call the right one as needed
    for event in events:
        add_to_table(event, cal_table, block_labels)

    return html_headers(cal_table.listreturn(headers=True))


def event_info(confitem_type='Show',
               filter_type=None,
               cal_times=(datetime(2016, 02, 5, 18, 00,
                                   tzinfo=pytz.timezone('UTC')),
                          datetime(2016, 02, 7, 00, 00,
                                   tzinfo=pytz.timezone('UTC'))),
               conference=None):
    '''
    Queries the database for scheduled events of type confitem_type,
    during time cal_times,
    and returns their important information in a dictionary format.
    '''
    if confitem_type in ['Panel', 'Movement', 'Lecture', 'Workshop']:
        filter_type, confitem_type = confitem_type, 'Class'
    elif confitem_type in ['Special Event',
                           'Volunteer Opportunity',
                           'Master Class',
                           'Drop-In Class']:
        filter_type, confitem_type = confitem_type, 'GenericEvent'

    import gbe.models as conf
    from scheduler.models import Location
    if not conference:
        conference = conf.Conference.current_conf()
    confitem_class = eval('conf.'+confitem_type)
    confitems_list = confitem_class.objects.filter(conference=conference)
    confitems_list = [confitem for confitem in confitems_list if
                      confitem.schedule_ready and confitem.visible]

    if filter_type is not None:
        confitems_list = [
            confitem for confitem in confitems_list if
            confitem.sched_payload['details']['type'] == filter_type]

    loc_allocs = []
    for l in Location.objects.all():
        loc_allocs += l.allocations.all()

    scheduled_events = [alloc.event for alloc in loc_allocs]

    for event in scheduled_events:
        start_t = event.start_time
        stop_t = event.start_time + event.duration
        if start_t > cal_times[1] or stop_t < cal_times[0]:
            scheduled_events.remove(event)

    scheduled_event_ids = [
        alloc.event.eventitem_id for alloc in scheduled_events]
    events_dict = {}
    for index in range(len(scheduled_event_ids)):
        for confitem in confitems_list:
            if scheduled_event_ids[index] == confitem.eventitem_id:
                events_dict[scheduled_events[index]] = confitem

    events = [{'title': confitem.title,
               'link': reverse('detail_view', urlconf='scheduler.urls',
                               args=[str(confitem.eventitem_id)]),
               'description': confitem.description,
               'start_time': event.start_time,
               'stop_time': event.start_time + confitem.duration,
               'location': event.location.room.name,
               'type': "%s.%s" % (
                   event.event_type_name,
                   event.confitem.sched_payload['details']['type'])}
              for (event, confitem) in events_dict.items()]
    return events


def select_day(days, day_name):
    '''
    Take a list of conference_days, return the one whose name is day_name
    Behavior is undefined if conference has more than one instance of a
    given day of week. This is a bug.
    '''
    return {date_format(d.day, "DAY_FORMAT"): d for d in days}.get(day_name, None)


def date_to_datetime(the_date):
    zero_hour = time(0)
    return utc.localize(datetime.combine(the_date, zero_hour))


def get_default_range():
    today = date_to_datetime(date.today())
    return (today + Duration(hours=8), today + Duration(hours=28))


def cal_times_for_conf(conference, day_name):
    from gbe.functions import get_conference_days  # late import, circularity
    days = get_conference_days(conference)

    if not days.exists():
        return get_default_range()
    if day_name:
        selected_day = select_day(days, day_name)
        if not selected_day:
            return get_default_range()
        day = date_to_datetime(selected_day.day)
        if day:
            return day + Duration(hours=8), day + Duration(hours=28)

    else:
        first_day = date_to_datetime(days.first().day)
        last_day = date_to_datetime(days.last().day)
        return (first_day + Duration(hours=8), last_day + Duration(hours=28))


def get_events_and_windows(conference):
    from scheduler.models import Event

    events = Event.objects.filter(
        max_volunteer__gt=0,
        eventitem__event__conference=conference
        ).exclude(
            eventitem__event__genericevent__type='Rehearsal Slot').order_by(
                'starttime')
    conf_windows = conference.windows()
    volunteer_event_windows = []

    for event in events:
        volunteer_event_windows += [{
            'event': event,
            'window': conf_windows.filter(
                day__day=event.starttime.date(),
                start__lte=event.starttime.time(),
                end__gt=event.starttime.time()).first()
            }]
    return volunteer_event_windows


def get_roles_from_scheduler(workeritems, conference):
    '''
    get the list roles for this set of worker items and this conference
    Based on the idea that 1 person is actually represented by multiple
    worker items
    '''
    roles = []
    from scheduler.models import ResourceAllocation
    for allocation in ResourceAllocation.objects.filter(
            resource__worker___item__in=workeritems):
        if allocation.event.eventitem.get_conference() == conference:
            roles += [allocation.resource.as_subtype.role]

    return list(set(roles))
