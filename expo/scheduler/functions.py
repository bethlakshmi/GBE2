# 2014.10.24 16:52:10 EDT
from table import table
from datetime import datetime
from datetime import timedelta
from calendar import timegm
from duration import Duration
from random import choice

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

def return_color_set(base_color = 'random'):
    '''
    Returns a complete set of colors for rendering HTML web pages, once each of Foreground,
    Background, Border, unseen link, seen link, and active link.  Either bases the colors off of
    a base color (optional), or it randomly selects one of the 140 named colors.  Accepts
    either 'random' to select a random color set, a HTML color name (one of 140), a HTML hex
    code (begining with #), or nothing.
    '''

    colors = {
            'AliceBlue': '#F0F8FF',
            'DarkOliveGreen': '#556B2F',
            'Indigo': '#4B0082',
            'MediumPurple': '#9370D8',
            'Purple': '#800080',
            'AntiqueWhite': '#FAEBD7',
            'DarkOrange': '#FF8C00',
            'Ivory': '#FFFFF0',
            'MediumSeaGreen': '#3CB371',
            'Red': '#FF0000',
            'Aqua': '#00FFFF',
            'DarkOrchid': '#9932CC',
            'Khaki': '#F0E68C',
            'MediumSlateBlue': '#7B68EE',
            'RosyBrown': '#BC8F8F',
            'AquaMarine': '#7FFFD4',
            'DarkRed': '#8B0000',
            'Lavender': '#E6E6FA',
            'MediumSpringGreen': '#00FA9A',
            'RoyalBlue': '#4169E1',
            'Azure': '#F0FFFF',
            'DarkSalmon': '#E9967A',
            'LavenderBlush': '#FFF0F5',
            'MediumTurquoise': '#48D1CC',
            'SaddleBrown': '#8B4513',
            'Beige': '#F5F5DC',
            'DarkSeaGreen': '#8FBC8F',
            'LawnGreen': '#7CFC00',
            'MediumVioletRed': '#C71585',
            'Salmon': '#FA8072',
            'Bisque': '#FFE4C4',
            'DarkSlateBlue': '#483D8B',
            'LemonChiffon': '#FFFACD',
            'MidnightBlue': '#191970',
            'SandyBrown': '#F4A460',
            'Black': '#000000',
            'DarkSlateGray': '#2F4F4F',
            'LightBlue': '#ADD8E6',
            'MintCream': '#F5FFFA',
            'SeaGreen': '#2E8B57',
            'BlanchedAlmond': '#FFEBCD',
            'DarkTurquoise': '#00CED1',
            'LightCoral': '#F08080',
            'MistyRose': '#FFE4E1',
            'SeaShell': '#FFF5EE',
            'Blue': '#0000FF',
            'DarkViolet': '#9400D3',
            'LightCyan': '#E0FFFF',
            'Moccasin': '#FFE4B5',
            'Sienna': '#A0522D',
            'BlueViolet': '#8A2BE2',
            'DeepPink': '#FF1493',
            'LightGoldenrodYellow': '#FAFAD2',
            'NavajoWhite': '#FFDEAD',
            'Silver': '#C0C0C0',
            'Brown': '#A52A2A',
            'DeepSkyBlue': '#00BFFF',
            'LightGray': '#D3D3D3',
            'Navy': '#000080',
            'SkyBlue': '#87CEEB',
            'BurlyWood': '#DEB887',
            'DimGray': '#696969',
            'LightGreen': '#90EE90',
            'OldLace': '#FDF5E6',
            'SlateBlue': '#6A5ACD',
            'CadetBlue': '#5F9EA0',
            'DodgerBlue': '#1E90FF',
            'LightPink': '#FFB6C1',
            'Olive': '#808000',
            'SlateGray': '#708090',
            'Chartreuse': '#7FFF00',
            'FireBrick': '#B22222',
            'LightSalmon': '#FFA07A',
            'OliveDrab': '#688E23',
            'Snow': '#FFFAFA',
            'Chocolate': '#D2691E',
            'FloralWhite': '#FFFAF0',
            'LightSeaGreen': '#20B2AA',
            'Orange': '#FFA500',
            'SpringGreen': '#00FF7F',
            'Coral': '#FF7F50',
            'ForestGreen': '#228B22',
            'LightSkyBlue': '#87CEFA',
            'OrangeRed': '#FF4500',
            'SteelBlue': '#4682B4',
            'CornFlowerBlue': '#6495ED',
            'Fuchsia': '#FF00FF',
            'LightSlateGray': '#778899',
            'Orchid': '#DA70D6',
            'Tan': '#D2B48C',
            'Cornsilk': '#FFF8DC',
            'Gainsboro': '#DCDCDC',
            'LightSteelBlue': '#B0C4DE',
            'PaleGoldenRod': '#EEE8AA',
            'Teal': '#008080',
            'Crimson': '#DC143C',
            'GhostWhite': '#F8F8FF',
            'LightYellow': '#FFFFE0',
            'PaleGreen': '#98FB98',
            'Thistle': '#D8BFD8',
            'Cyan': '#00FFFF',
            'Gold': '#FFD700',
            'Lime': '#00FF00',
            'PaleTurquoise': '#AFEEEE',
            'Tomato': '#FF6347',
            'DarkBlue': '#00008B',
            'GoldenRod': '#DAA520',
            'LimeGreen': '#32CD32',
            'PaleVioletRed': '#D87093',
            'Turquoise': '#40E0D0',
            'DarkCyan': '#008B8B',
            'Gray': '#808080',
            'Linen': '#FAF0E6',
            'PapayaWhip': '#FFEFD5',
            'Violet': '#EE82EE',
            'DarkGoldenRod': '#B8860B',
            'Green': '#008000',
            'Magenta': '#FF00FF',
            'PeachPuff': '#FFDAB9',
            'Wheat': '#F5DEB3',
            'DarkGray': '#A9A9A9',
            'GreenYellow': '#ADFF2F',
            'Maroon': '#800000',
            'Peru': '#CD853F',
            'White': '#FFFFFF',
            'DarkGreen': '#006400',
            'HoneyDew': '#F0FFF0',
            'MediumAquaMarine': '#66CDAA',
            'Pink': '#FFC0CB',
            'WhiteSmoke': '#F5F5F5',
            'DarkKhaki': '#BDB76B',
            'HotPink': '#FF69B4',
            'MediumBlue': '#0000CD',
            'Plum': '#DDA0DD',
            'Yellow': '#FFFF00',
            'DarkMagenta': '#8B008B',
            'IndianRed': '#CD5C5C',
            'MediumOrchid': '#BA55D3',
            'PowderBlue': '#B0E0E6',
            'YellowGreen': '#9ACD32',
            }
    if base_color == 'random':
        from random import choice
        base_color = choice(colors)

