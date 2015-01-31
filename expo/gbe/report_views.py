# View functions for reporting
from django.shortcuts import render, get_object_or_404, render_to_response

import gbe.models as conf
import scheduler.models as sched
import ticketing.models as tix

import csv
from reportlab.pdfgen import canvas
from gbe.functions import *

def staff_area(request, area):
    '''
    Generates a staff area report: volunteer opportunities scheduled, volunteers scheduled, 
    sorted by time/day
    See ticket #250
    '''
    pass

def env_stuff(request):
    '''
    Generates an envelope-stuffing report. 
    See ticket #251 for details. 
    '''
    pass

    
def review_act_techinfo(request, show_id=1):
    '''
    Show the list of act tech info for all acts in a given show 
    '''
    reviewer = validate_perms(request, ('Tech Crew',))
    
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.  I can still show a list of shows this way.
    try:
        show = conf.Show.objects.get(eventitem_id=show_id)
        acts = show.scheduler_events.first().get_acts()

    except:
        show = None
        acts = []
    
    '''
    location = show.scheduler_events.first().location
    if location.describe == 'Theater':
        sub_header = ['Cue #', 'Cue off of', 'Follow spot', 'Center Spot','Backlight', 'Cyc Light', 'Wash', 'Sound']
    else:
        sub_header = ['Cue #', 'Cue off of', 'Follow spot', 'Wash', 'Sound']
    '''

    return render (request, 'gbe/act_tech_review.tmpl',
                  {'this_show': show, 'acts': acts, 'all_shows': conf.Show.objects.all()})
                    
