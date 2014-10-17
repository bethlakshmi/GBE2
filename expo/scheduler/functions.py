from table import table
from datetime import datetime
#from gbe.duration import Duration
from duration import Duration

def TablePrep(Events, Duration):
    '''
    Accepts an unordered list of events, and returns a table ready to be
    sent to the Sched_Display template.  Events is a list, with each entry
    having properties for the appropriate information for each event, 
    including Text (event title or name), Link (URL for the event 
    information), start and stop time, and event type.  Type is used to
    determine what colors each event is displayed with.  Duration is the
    length, in minutes, of each cell in the table.  StartTime and StopTime
    are both DateTime objects (integers with 
    '''

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

        min = int(Event['StartTime'].minute / Duration) * Duration
        StartTime = Event['StartTime'].strftime('%a %I:'+ str(min) +' %p')
        starttime = Event['StartTime'].hour *60 + Event['StartTime'].minute
        stoptime = Event['StopTime'].hour *60 + Event['StopTime'].minute
        time = int(starttime / Duration) * Duration
        location = Event['Location']

        if (location) not in Table._col_list:
            Table.addcol(location)

        if StartTime not in Table._row_list:
        ###  Fix calc of StartTime to be added to row list
        ###  Needs to work on intervals of Duration, so that an event that
        ###  begins at 9:05 and one that starts at 9:00 end up in the same
        ###  hour block
            Table.addrow(StartTime)
            times.append(starttime)
            times.sort()
        starttime = Event['StartTime'].hour *60 + Event['StartTime'].minute
        stoptime = Event['StopTime'].hour *60 + Event['StopTime'].minute
        time = int(starttime / Duration) * Duration

        Cell = {}
        Cell['Text'] = Event['Text']
        Cell['Link'] = Event['Link']
        
        if ['Color'] not in dir(Event):
            if Event['Type'] in types.keys():
                Cell['FG_Color'], Cell['BG_Color'], Cell['Border_Color'] = types[Event['Type']]
            else:
                color_set = choice(colors)
                colors.remove(color_set)
                Cell['FG_Color'], Cell['BG_Color'], Cell['Border_Color'] = color_set
                types[Event['Type']] = color_set

        cells = int((starttime - stoptime)/Duration +.8)
        if cells == 1:
            Cell['Borders'] = ['Top', 'Left', 'Right', 'Bottom']
            Table[location, time] = Cell
        else:
            Cell['Borders'] = ['Top', 'Left', 'Right']
            Table[location, time] = Cell
            cells = cells - 1
            while cells != 1:
                time = time + Duration
                Cell['Text'], Cell['Link'] = '', ''
                Cell['Borders'] = ['Left', 'Right']
                Table[location, time] = Cell
            time = time + Duration
            Cell['Text'], Cell['Link'] = '', ''
            Cell['Borders'] = ['Left', 'Right', 'Bottom']
            Table[location, time] = Cell
    return Table
