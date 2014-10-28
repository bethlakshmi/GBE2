# 2014.10.24 16:52:10 EDT
from table import table
from datetime import datetime
from datetime import timedelta
from calendar import timegm
from duration import Duration
from random import choice

def TablePrep(Events, Duration):
    """
    Accepts an unordered list of events, and returns a table ready to be
    sent to the Sched_Display template.  Events is a list, with each entry
    having properties for the appropriate information for each event, 
    including Text (event title or name), Link (URL for the event 
    information), start and stop time, and event type.  Type is used to
    determine what colors each event is displayed with.  Duration is the
    length, in minutes, of each cell in the table.  StartTime and StopTime
    are both DateTime objects (integers with 
    """
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
                (Cell['FG_Color'], Cell['BG_Color'], Cell['Border_Color'],) = types[Event['Type']]
            else:
                color_set = choice(colors)
                colors.remove(color_set)
                (Cell['FG_Color'], Cell['BG_Color'], Cell['Border_Color'],) = color_set
                types[Event['Type']] = color_set
        cells = int((stoptime - starttime) / Duration / 60 + 0.8)
        print cells
        if cells == 1:
            Cell['Borders'] = ['Top',
             'Left',
             'Right',
             'Bottom']
            Table[starttime, location] = Cell
        elif cells >= 2:
            Cell['Borders'] = ['Top', 'Left', 'Right']
            if starttime not in Table.rowlist:
                Table.addrow(starttime)
            Table[starttime, location] = Cell
            cells = cells - 1
            while cells >= 2:
                starttime = starttime + (Duration * 60)
                (Cell['Text'], Cell['Link'],) = ('', '')
                Cell['Borders'] = ['Left', 'Right']
                if starttime not in Table.rowlist:
                    Table.addrow(starttime)
                Table[starttime, location] = Cell
                cells = cells - 1

            starttime = starttime + (Duration * 60)
            (Cell['Text'], Cell['Link'],) = ('', '')
            Cell['Borders'] = ['Left', 'Right', 'Bottom']
            if starttime not in Table.rowlist:
                Table.addrow(starttime)
            Table[starttime, location] = Cell

    return Table.listreturn()
