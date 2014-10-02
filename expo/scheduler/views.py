from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template import loader, RequestContext
from scheduler.models import *
from scheduler.forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.forms.models import inlineformset_factory
import gbe_forms_text
from django.core.urlresolvers import reverse


# Create your views here.


def class_schedule(request):
    '''
    Schedule a class.
    '''

    pass

@login_required
def event_schedule(request):
    '''
    Schedule an event.
    '''

    page_title = 'Schedule an Event'
    view_title = 'Add an Event to the Calendar'
    submit_button = 'Schedule Event'
    update_button = 'Update Event Info'    

    try:
        event_id = request.event_id
    except:
        pass

    form = 

def panel_schedule(request):
    '''
    Schedule a panel.
    '''

    pass

def calendar(request, cal_format = 'Block'):
    '''
    Top level calendar object.  Overall calendar for a site, sets some options,
    then calls calendar_view.
    '''

    pass

def calendar_view(request, cal_type = 'Event', cal_format = 'Block'):
    '''
    Accepts a calendar type, and renders a calendar for that type.  Type can be
    an event class, an event instance (shows what is scheduled within that
    event), an event reference (shows a calendar of just every instance of
    that event), or a schedulable items (which shows a calendar for that item).
    '''

    pass

