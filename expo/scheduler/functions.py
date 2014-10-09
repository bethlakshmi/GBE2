from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from table import table

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

    HTML_Object = '''
{% extends "base.html" %}
    '''

    ###  First, Table Title.
    ###  Yeah, Yeah, I know, not dealing with color yet.  Need to figure out
    ###  CSS tags, etc.
    try:
        try:
            HTML_Object = HTML_Object + ''' 
{% block title %}'''+ Table_Name[Text] +'''{% endblock %}
{% block content %}
<h1><a href="'''+ Table_Name[Link] +'''">+''' Table_Name[Text] +'''</a></h1>
{% endblock %}
''' 
        except:
            HTML_Object = HTML_Object + ''' 
{% block title %}'''+ Table_Name[Text] +'''{% endblock %}
{% block content %}
<h1>'''+ Table_Name[Text] +'''</h1>
{% endblock %}
''' 
    except:
        pass

    ###  Then we deal with the column titles.
    ###  Also, I know that I need to move the X and Y column
    ###  titles around, and put the table into a sub-block.  Later,
    ###  after getting the table to just f$%*!@g work.
    try:
                try:
            HTML_Object = HTML_Object + ''' 
{% block title %}'''+ X_Name[Text] +'''{% endblock %}
{% block content %}
<h2><a href="'''+ X_Name[Link] +'''">+''' X_Name[Text] +'''</a></h2>
{% endblock %}
''' 
        except:
            HTML_Object = HTML_Object + ''' 
{% block title %}'''+ X_Name[Text] +'''{% endblock %}
{% block content %}
<h2>'''+ X_Name[Text] +'''</h2>
{% endblock %}
''' 
    except:
        pass

    try:
                try:
            HTML_Object = HTML_Object + ''' 
{% block title %}'''+ Y_Name[Text] +'''{% endblock %}
{% block content %}
<h2><a href="'''+ Y_Name[Link] +'''">+''' Y_Name[Text] +'''</a></h2>
{% endblock %}
''' 
        except:
            HTML_Object = HTML_Object + ''' 
{% block title %}'''+ Y_Name[Text] +'''{% endblock %}
{% block content %}
<h2>'''+ Y_Name[Text] +'''</h2>
{% endblock %}
''' 
    except:
        pass

    ###  *SIGH*  Now for the hard part.  Dealing with the table.  If it was
    ###  not for the table object type, this would be annoying.
    try:
        HTML_Object = HTML_Object + '''
<table>
'''
        for row in Table._row_list:
            HTML_Object = HTML_Object + '''
<tr>
'''
            for cell in row:
                if 'BG_Color' in cell.keys():
                    entry = '''
<td BGCOLOR = '''+ cell[BG_Color] +'''>
'''
                else
                    entry = '''
<td>
'''
                try:
                    entry = entry + '<li><a href="' + \
                        cell[Link]+'">'+ cell[Text] +'</a><li>'
                except:
                    entrey = entry + cell[Text]
                entry = entry + '''
</td>
'''
                HTML_Object = HTML_Object + entry
            HTML_Object = HTML_Object + '''
</tr>
'''
        HTML_Object = HTML_Object + '''
</table> 
'''
    except:
        ###  I guess this is what I want to do....
        pass

    return HTML_Object
