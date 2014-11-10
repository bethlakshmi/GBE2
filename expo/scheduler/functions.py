from table import table
from datetime import timedelta
from datetime import time
from datetime import datetime
from calendar import timegm
from gbe.duration import Duration
from gbe.duration import timedelta_to_duration
from random import choice
import math


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
#        cal_start = sorted(events, key = lambda event:event['starttime'])[0]
        cal_start = sorted([event['starttime'] for event in events])[0]
    elif instanceof(cal_start, time):
        cal_start = datetime.combine(datetime.min,cal_start)
    if not cal_stop:

        
        cal_stop = sorted([event['stoptime'] for event in events])[-1]
 #       cal_stop = sorted(events, key = lambda event:event['stoptime'])[-1]
    elif instanceof(cal_stop, datetime): 
        cal_stop = datetime.combine(datetime.min,cal_stop)
    if cal_stop < cal_start:    # assume that we've gone past midnight
        cal_stop += timedelta(days=1) 
    if trim_to_block_size:
        pass  # TO DO
    
    schedule_duration = timedelta_to_duration(cal_stop-cal_start)
    blocks_count = int(math.ceil (schedule_duration/block_size))
    block_labels = [(cal_start + block_size * b).strftime("%H:%M") for b in range(blocks_count)]
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


    if event['starttime'] < schedule_start:
        relative_start = Duration(seconds=0)
    else:
        relative_start = event['starttime'] - schedule_start
    if event['stoptime'] > schedule_stop:
        working_stoptime = schedule_stop
    else:
        working_stoptime = timedelta_to_duration(event['stoptime'] - schedule_start)

    
    event['startblock'] = timedelta_to_duration(relative_start) // block_size
    event['startlabel'] = block_labels[event['startblock']]
    event['rowspan'] = int(math.ceil(working_stoptime / block_size))-event['startblock']

    


def overlap_check(events):
    '''
    Return a list of event tuples such that all members of a tuple are in the same room
    and stop time of one event overlaps with at least one other member of the tuple
    '''
    overlaps = []
    for location in set([e['location'] for e in events]):
        prev_stop = 0
        prev_event = None
        conflict_set = set()
        location_events = sorted([event for event in events if event['location'] == location], 
                                 key = lambda event:event['startblock'])
        for event in location_events:
            if event['startblock'] < prev_stop:
                conflict_set = conflict_set + prev_event
                conflict_set = conflict_set + event
            else:
                if len(conflict_set) >0:
                    overlaps += tuple(conflict_set)
                    conflict_set = set()
            prev_stop = event['startblock'] + event['rowspan'] 
            prev_event = event
        if len(conflict_set) >0:
            overlaps += tuple (conflict_set)
            conflict_set = set()
    return overlaps
            


# default handling of overlapping events:
## public calendars: do not show any overlapping events
## Second pass: display in calendar with fancy trickery. (handwave, handwave)
## admin calendars: combine overlapping events into "OVERLAP" event
## possibly also offer calendar showing only overlaps


def add_to_table(event, table, block_labels):
    '''
    Insert event into appropriate cell in table
    If event occupies multiple blocks, insert "placeholder" object in 
    subsequent table cells
    '''
    table[event['location'], block_labels[event['startblock']]] = '<td rowspan=%d class=%s>%s</td>'%(event['rowspan'], event['html'], event.get('css_class', ''))
    for i in range(1, event['rowspan']):
        table[event['location'], block_labels[event['startblock']+i]] = '&nbsp;'


def tablePrep(events, block_size, time_format="{1:0>2}:{2:0>2}", cal_start=None, cal_stop=None, col_heads=None):
    '''
    Generate a calendar table based on submitted events
    
    '''
    block_labels, cal_start, cal_stop = init_time_blocks(events, block_size, time_format, cal_start, cal_stop)
    if not col_heads:
        col_heads = init_column_heads(events)
    cal_table = table(rows=block_labels, columns=col_heads)
    events = filter (lambda e:  ((cal_start <= e['starttime'] < cal_stop)) or 
                     ((cal_start < e['stoptime'] <= cal_stop)), events)
    for event in events:
        normalize(event, cal_start, cal_stop, block_labels, block_size)
    overlaps = overlap_check(events)
    # don't worry about handling now, 
    # but write overlap handlers and call the right one as needed
    for event in events:
        add_to_table(event, cal_table, block_labels)
    return cal_table.listreturn()
    

def TablePrep(Events, Duration):
    '''
    Accepts an unordered list of events, and returns a table ready to be
    sent to the Sched_Display template.  Events is a list, with each entry
    having properties for the appropriate information for each event, 
    including Text (event title or name), Link (URL for the event 
    information), start and stop time, and event type.  Type is used to
    determine what colors each event is displayed with.  Duration is the
    length, in minutes, of each cell in the table.  StartTime and StopTime
    are both DateTime objects.
    '''

    PrettyFormat = '%a %I:%M %p'
    Table = table([], [])
    times = []
    colors = [
        {'FG_Color': 'Teal', 'BG_Color': 'Red', 'Border_Color': 'DarkRed'},
        {'FG_Color': 'SeaGreen', 'BG_Color': 'HotPink', 'Border_Color': 'MediumVioletRed'},
        {'FG_Color': 'Naw', 'BG_Color': 'LightSalmon', 'Border_Color': 'DarkOrange'},
        {'FG_Color': 'CadetBlue', 'BG_Color': 'Khaki', 'Border_Color': 'Gold'},
        {'FG_Color': 'SeaGreen', 'BG_Color': 'Amethyst', 'Border_Color': 'DarkViolet'},
        {'FG_Color': 'Indigo', 'BG_Color': 'SpringGreen', 'Border_Color': 'ForrestGreen'},
        {'FG_Color': 'SaddleBrown', 'BG_Color': 'RoyalBlue', 'Border_Color': 'DarkBlue'},
        {'FG_Color': 'DarkOliveGreen', 'BG_Color': 'Aquamarine', 'Border_Color': 'SteelBlue'},
        {'FG_Color': 'DarkCyan', 'BG_Color': 'SandyBrown', 'Border_Color': 'DarkGoldenrod'},
        {'FG_Color': 'Black', 'BG_Color': 'Silver', 'Border_Color': 'DarkSlateGray'}
        ]
    types = {}
    for Event in Events:
        min = str(int(Event['StartTime'].minute / Duration) * Duration)
        if len(min) == 1:
            min = '0' + min
        Time = Event['StartTime']
        starttime = timegm(Event['StartTime'].utctimetuple())
        stoptime = timegm(Event['StopTime'].utctimetuple())
        time = int(starttime / Duration) * Duration
        location = Event['Location']
        if location not in Table.collist:
            Table.addcol(location)
        if starttime not in Table.rowlist:
            Table.addrow(starttime)
            times.append(starttime)
            times.sort()
        Cell = {}
        Cell['Text'] = Event['Text']
        Cell['Link'] = Event['Link']
        if ['Color'] not in dir(Event):
            if Event['Type'] in types.keys():
                Cell['FG_Color'], Cell['BG_Color'], Cell['Border_Color'] = types[Event['Type']]
            else:
                color_set = choice(colors)
                Cell['FG_Color'], Cell['BG_Color'], Cell['Border_Color'] = \
                    color_set['FG_Color'], color_set['BG_Color'], color_set['Border_Color']
                color_set = choice(colors)
                Cell['Alink_Color'], Cell['Vlink_Color'], Cell['Link_Color'] = \
                    color_set['FG_Color'], color_set['BG_Color'], color_set['Border_Color']
        cells = int((stoptime - starttime) / Duration / 60 + 0.8)
        if cells == 1:
            Cell['Borders'] = ['Top', 'Left', 'Right', 'Bottom']
            if starttime not in Table.rowlist:
                Table.addrow(starttime)
            Table[starttime, location] = Cell
        elif cells >= 2:
            Cell['Borders'] = ['Top', 'Left', 'Right']
            if starttime not in Table.rowlist:
                Table.addrow(starttime)
            print starttime, cells
            Table[starttime, location] = Cell
            cells = cells - 1
            while cells >= 2:
                starttime = starttime + (Duration * 60)
                del Cell['Text'], Cell['Link']
                Cell['Borders'] = ['Left', 'Right']
                if starttime not in Table.rowlist:
                    Table.addrow(starttime)
                print starttime, cells
                Table[starttime, location] = Cell
                cells = cells - 1

            starttime = starttime + (Duration * 60)
            del Cell['Text'], Cell['Link']
            Cell['Borders'] = ['Left', 'Right', 'Bottom']
            if starttime not in Table.rowlist:
                Table.addrow(starttime)
            print starttime, cells
            Table[starttime, location] = Cell
         
    return Table.listreturn('column')
