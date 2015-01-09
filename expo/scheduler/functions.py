from table import table
from datetime import timedelta
from datetime import time
from datetime import datetime
from calendar import timegm
from gbe.duration import Duration
from gbe.duration import timedelta_to_duration
from random import choice
import math
try: from expo.settings import DATETIME_FORMAT
except: DATETIME_FORMAT = None

from django.core.urlresolvers import reverse
import pytz

conference_days = ( 
    (datetime(2015, 02, 19).strftime('%Y-%m-%d'), 'Thursday'),
    (datetime(2015, 02, 20).strftime('%Y-%m-%d'), 'Friday'),
    (datetime(2015, 02, 21).strftime('%Y-%m-%d'), 'Saturday'),
    (datetime(2015, 02, 22).strftime('%Y-%m-%d'), 'Sunday'),
)



time_start = 8 * 60
time_stop = 24 * 60  

conference_times = [(time(mins/60, mins%60), time(mins/60, mins%60).strftime("%I:%M %p")) 
                    for mins in range (time_start, time_stop, 30)]

conference_dates = {"Thursday":"2015-02-19" ,
              "Friday":"2015-02-20",
              "Saturday": "2015-02-21" ,
              "Sunday": "2015-02-22"}



def set_time_format(events = None, days = 0):
    '''
    Returns a default time format which prepends a day if day, date,
    etc is not included AND a test for included days is greater then
    one.  Uses the default set in settings.py, and if that is absent,
    set it to 12 hour and min with AM and PM (%I:%M %p).  Can accept a
    dictionary of events with the datetime info in it, or a number of
    days covered by the format.  Numbers greater then 2 cause the name
    of the day to be prepended to the format.  Will add similar for
    months later.
    '''

    try: from expo.settings import DATETIME_FORMAT
    except: DATETIME_FORMAT = None

    if type(events) == type({}) and days == 0:
        for event in events:
            day = event['start_time'].day
            if day not in days:
                days.append(day)
        days = len(days)

    if days <= 1:
        if DATETIME_FORMAT == None:
            DATETIME_FORMAT = "%I:%M %p"
    else:
        if DATETIME_FORMAT == None:
            DATETIME_FORMAT = "%a, %I:%M %p"
        else:
            testValue = False
            for dayValue in  ('%a', '%A', '%w', '%d', '%j'): # Test for formats that print the day
                if dayValue in DATETIME_FORMAT: testValue = True
            if not testValue: DATETIME_FORMAT = '%a, ' + DATETIME_FORMAT
    return DATETIME_FORMAT

def init_time_blocks(events, block_size, time_format,
                     cal_start= None, cal_stop = None,
                     trim_to_block_size=True, offset=None ):
    '''
    Find earliest start time and latest stop time and generate a list of 
    schedule blocks enclosing these. 
    trim_to_block_size  ensures that the starting block starts on an integer 
    multiple of block_size
    offset: not implemented. Will allow setting an offset for schedule blocks
    cal_start and cal_stop are preset values for start time and stop time, as datetime objects
    (will allow for time objects, but not yet)
    If provided, they are assumed to be correct. (ie, we don't adjust them, just use them)
    
    '''
    if not cal_start:
#        cal_start = sorted(events, key = lambda event:event['start_time'])[0]
        cal_start = sorted([event['start_time'] for event in events])[0]
    elif isinstance(cal_start, time):
        cal_start = datetime.combine(datetime.min,cal_start)

    if not cal_stop:
        cal_stop = sorted([event['stop_time'] for event in events])[-1]
 #       cal_stop = sorted(events, key = lambda event:event['stop_time'])[-1]
    elif isinstance(cal_stop, time): 
        cal_stop = datetime.combine(datetime.min,cal_stop)

    if cal_stop < cal_start:    # assume that we've gone past midnight
        cal_stop += timedelta(days=1) 
    if trim_to_block_size:
        pass  # TO DO
    
    schedule_duration = timedelta_to_duration(cal_stop-cal_start)
    blocks_count = int(math.ceil (schedule_duration/block_size))
    block_labels = [(cal_start + block_size * b).strftime(time_format) for b in range(blocks_count)]
    return block_labels, cal_start, cal_stop

def init_column_heads(events):
    '''
    Scan events and return list of room names. 
    '''
    return list(set([e['location'] for e in events]))




def normalize(event, schedule_start, schedule_stop, block_labels, block_size):
    '''
    Set a startblock and rowspan for event such that startblock is the
    earliest block containing the event's start time, and rowspan is the number of blocks it occupies
    block_size should be a Duration
    '''
    from gbe.duration import timedelta_to_duration


#    schedule_start = Duration(hours = schedule_start.hour, 
#                      minutes = schedule_start.minute, 
#                      seconds = schedule_start.second)
#    schedule_stop = Duration(hours = schedule_stop.hour, 
#                      minutes = schedule_stop.minute, 
#                      seconds = schedule_stop.second)


    if event['start_time'] < schedule_start:
        relative_start = Duration(seconds=0)
    else:
        relative_start = event['start_time'] - schedule_start
    if event['stop_time'] > schedule_stop:
        working_stop_time = schedule_stop
    else:
        working_stop_time = timedelta_to_duration(event['stop_time'] - schedule_start)

    
    event['startblock'] = timedelta_to_duration(relative_start) // block_size
    event['startlabel'] = block_labels[event['startblock']]
    event['rowspan'] = int(math.ceil(working_stop_time / block_size))-event['startblock']

    


def overlap_check(events):
    '''
    Return a list of event tuples such that all members of a tuple are in the same room
    and stop time of one event overlaps with at least one other member of the tuple
    '''
    overlaps = []
    for location in set([e['location'] for e in events]):
        prev_stop = 0
        prev_event = None
        conflict_set = {}
        location_events = sorted([event for event in events if event['location'] == location], 
                                 key = lambda event:event['startblock'])
        for event in location_events:
            if event['startblock'] < prev_stop:
                conflict_set[prev_event] = event
            else:
                if len(conflict_set) >0:
                    overlaps += conflict_set.items()
                    conflict_set = {}
            prev_stop = event['startblock'] + event['rowspan'] 
            prev_event = event
        if len(conflict_set) >0:
            overlaps += conflict_set.items()
            conflict_set = {}
    return overlaps
            


# default handling of overlapping events:
## public calendars: do not show any overlapping events
## Second pass: display in calendar with fancy trickery. (handwave, handwave)
## admin calendars: combine overlapping events into "OVERLAP" event
## possibly also offer calendar showing only overlaps


def add_to_table(event, table, block_labels):
    '''
    Insert event into appropriate cell in table
    If event occupies multiple blocks, insert "placeholder" in 
    subsequent table cells (nonbreaking space)
    '''
    table[event['location'], block_labels[event['startblock']] ] = '<td rowspan=%d class=\'%s\'>%s</td>' %(event['rowspan'], event.get('css_class'), event.get('html', 'FOO'))
    for i in range(1, event['rowspan']):
        table[event['location'], block_labels[event['startblock']+i]] = '&nbsp;'

def htmlPrep(event):
    '''
    If an event object does not have a HTML table block set up, this will
    generate one.
    '''

    html = '<li><a href=\'%s\'>%s</a></li>' %(event['link'], event['title'])
    if 'short_desc' in event.keys():
        #  short_desc is a short description, which is optional
        html = html+event['short_desc']
    return html

def htmlHeaders(table, headerStart = '<TH>', headerEnd = '</TH>'):
    '''
    Checks the header positions for a table, rendered as a list of lists, for HTML tags,
    and adds '<TH>' + cell + '</TH>' if they are absent.
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

def tablePrep(events, block_size, time_format=None, cal_start=None, cal_stop=None, col_heads=None):
    '''
    Generate a calendar table based on submitted events
    
    '''

    if time_format == None: time_format = set_time_format(events)
    block_labels, cal_start, cal_stop = init_time_blocks(events, block_size, time_format, cal_start, cal_stop)
    if not col_heads:
        col_heads = init_column_heads(events)
    cal_table = table(rows=block_labels, columns=col_heads, default = '<td></td>')
    events = filter (lambda e:  ((cal_start <= e['start_time'] < cal_stop)) or 
                     ((cal_start < e['stop_time'] <= cal_stop)), events)

    for event in events:
        normalize(event, cal_start, cal_stop, block_labels, block_size)
        if 'html' not in event.keys():
            event['html'] = htmlPrep(event)

    #overlaps = overlap_check(events)
    # don't worry about handling now, 
    # but write overlap handlers and call the right one as needed
    for event in events:
        add_to_table(event, cal_table, block_labels)

    return htmlHeaders(cal_table.listreturn(headers = True))

def event_info(confitem_type = 'Show', 
        filter_type = None,
        cal_times = (datetime(2015, 02, 20, 18, 00, tzinfo=pytz.timezone('UTC')),
        datetime(2015, 02, 23, 00, 00, tzinfo=pytz.timezone('UTC')))):
    '''
    Queries the database for scheduled events of type confitem_type, during time cal_times,
    and returns their important information in a dictionary format.
    '''

    if confitem_type in ['Panel', 'Movement', 'Lecture', 'Workshop']:
        filter_type, confitem_type = confitem_type, 'Class'

    import gbe.models as conf
    from scheduler.models import Location
    
    if confitem_type=='All':
        confitems_list = conf.Event.objects.all()
    else:
        confitem_class = eval ('conf.'+confitem_type)
        confitems_list = confitem_class.objects.all()
        
    confitems_list = [confitem for confitem in confitems_list if confitem.schedule_ready]

    if filter_type != None:
        confitems_list = [confitem for confitem in confitems_list if confitem.sched_payload['details']['type'] \
            == filter_type]

    loc_allocs = []
    for l in Location.objects.all():
        loc_allocs += l.allocations.all()

    scheduled_events = [alloc.event for alloc in loc_allocs]

    for event in scheduled_events:
         start_t = event.start_time
         stop_t = event.start_time + event.duration
         if start_t > cal_times[1] or stop_t < cal_times[0]:
             scheduled_events.remove(event)

    scheduled_event_ids = [alloc.event.eventitem_id for alloc in scheduled_events]    
    events_dict = {}
    for index in range(len(scheduled_event_ids)):
        for confitem in confitems_list:
            if scheduled_event_ids[index] == confitem.eventitem_id:
                events_dict[scheduled_events[index]] = confitem

    events = [{'title': confitem.title,
               'link' : reverse('detail_view', urlconf='scheduler.urls', 
                   args = [str(confitem.eventitem_id)]),
               'description': confitem.description,
               'start_time':  event.start_time,
               'stop_time':  event.start_time + confitem.duration,
               'location' : event.location.room.name,
            }
        for (event, confitem) in events_dict.items()]

    return events

def day_to_cal_time(day = 'Saturday', week = datetime(2015, 02, 19,tzinfo=pytz.timezone('UTC'))):
    '''
    Accepts a day of the week, and returns the hours for that day as a datetime tuple.  Can also accept a datetime
    for a particular week.
    '''

    conference_days = ['Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday']  
        # Eventually change this to a call to the master conference event to determine its first day
         
    #  we are dealing w/ ISO 8601 week, which start on Monday at 0, so Thursday is 3
    if week.weekday() < 3:
        shift = 3 - week.weekday()
        week = week + duration(shift * 60 * 60 * 24)
    elif week.weekday() > 3:
        shift = week.weekday() - 3
        week = week - duration(shift * 60 * 60 * 24)

    return_day = week + Duration(days = [i for i, x in enumerate(conference_days) if x == day][0])

    cal_times = (return_day + Duration(hours = 8), return_day + Duration(hours = 28))
    return cal_times
    
