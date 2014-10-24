#from django.shortcuts import render, get_object_or_404, render_to_response
#from django.http import HttpResponse, HttpResponseRedirect
from table import table

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

    Duration = float(Duration)
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

        location = Event['Location']
        if (location) not in Table._col_list:
            Table.addcol(location)

        if (Event['StartTime'] / Duration) not in Table._row_list:
        ###  Fix calc of StartTime to be added to row list
        ###  Needs to work on intervals of Duration, so that an event that
        ###  begins at 9:05 and one that starts at 9:00 end up in the same
        ###  hour block
            Table.addrow(Event['StartTime'])
            times.append(Event['StartTime'])
            times.sort()
        time = (Event['StartTime'] / Duration) * Duration

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

        cells = int((Event['StopTime'] - Event['StartTime'])/Duration +.8)
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

def HtmlSchedDisply(Table_Name, X_Name, Y_Name, Table):
    '''
    This function displays a table of cells which get rendered into an HTML
    table.  Table_Name, X_Name, and Y_Name are dictionaries that describes
    the titles for the table overall, the X columns, and the Y columns.
    The cells of these dictionaires can contain :
        Text - The text name of the table, no title if absent
        Link - URL for the table name, just a title if absent
        BG_Color - background color for the text, white if absent
        FG_Color - foreground color for the text, black if absent
    Table is a table object that contains dictionaries in each cell.  The
    top and left most column and row are assumed to be headers, but do not
    need to be.  The possible entries in the cells are:
        Link - URL for the cell to point to.  '' or None is used to not have
            link, or optional
        Text - Text displayed with the link, or as a title
        Link_Color - Color the link is rendered in
        BG_Color - background color - defaults to white if absent
        FG_Color - foreground color - defaults to black if absent
        Borders - List of which borders need to be drawn in, can be:
            'Top', 'Bottom', 'Left', 'Right'
        Border_Color - color borders are drawn in, defaults to black
    The function returns an object ready to be rendered into HTML.
    '''

    n = '    '   #  Use for Indentation
    HTML_Object = '''{% extends "base.html" %}'''

    ###  First, Table Title.
    ###  Yeah, Yeah, I know, not dealing with color yet.  Need to figure out
    ###  CSS tags, etc.
    try:
        try:
            HTML_Object = HTML_Object +'''
{% block title %}'''+ Table_Name['Text'] +'''{% endblock %}
{% block content %}
<h1><a href="'''+ Table_Name['Link'] +'''">'''+ Table_Name['Text'] +'''</a></h1>
{% endblock %}''' 
        except:
            HTML_Object = HTML_Object + ''' 
{% block title %}'''+ Table_Name['Text'] +'''{% endblock %}
{% block content %}
<h1>'''+ Table_Name['Text'] +'''</h1>
{% endblock %}''' 
    except:
        pass

    ###  Then we deal with the column titles.
    ###  Also, I know that I need to move the X and Y column
    ###  titles around, and put the table into a sub-block.  Later,
    ###  after getting the table to just f$%*!@g work.
    try:
        try:
            HTML_Object = HTML_Object + ''' 
<table>
<CAPTION ALIGN="top"><li><a href="'''+ X_Name['Link'] +'''">'''+ X_Name['Text'] +'''</a></li></CAPTION>'''
        except:
            HTML_Object = HTML_Object + ''' 
<table>
<CAPTION ALIGN="top">'''+ X_Name['Text'] +'''</CAPTION>''' 
    except:
        pass

    ###  Y column name would go here, but I do not know how to deal with
    ###  that yet.

    ###  *SIGH*  Now for the hard part.  Dealing with the table.  If it was
    ###  not for the table object type, this would be annoying.
    
    for row in Table._row_list:
        row_data = Table.getrow(row)
        HTML_Object = HTML_Object + '''
<tr>'''
        for cell in row_data:
            if type(cell) == type({}):
                if 'BG_Color' in cell.keys():
                    entry = '''
<td { BgColor = '''+ cell['BG_Color']+ ''';
'''
                else:
                    entry = '''
<td {'''
                for side in cell['Borders']:
                    if side in ('Top', 'Bottom', 'Left', 'Right'):
                        entry = entry + '    Border-'+ side +': Solid 2px '+ \
                            cell['Border_Color'] +''';
'''
                    else:
                        entry = entry + 'Border-'+ side + ''': Blank;'''
                entry = entry + '''    }\n'''
                try:
                    entry = entry + '<li><a href="' + \
                        cell['Link']+'">'+ cell['Text'] +'</a><li>'
                except:
                    entry = entry + cell['Text']
                entry = entry + '''</td>'''
                HTML_Object = HTML_Object + entry
        HTML_Object = HTML_Object + '''
</tr>'''
    HTML_Object = HTML_Object + '''
</table> '''

    return HTML_Object
