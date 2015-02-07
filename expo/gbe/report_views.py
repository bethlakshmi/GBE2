# View functions for reporting
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404

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
    
    return render (request, 'gbe/act_tech_review.tmpl',
                  {'this_show': show, 'acts': acts, 'all_shows': conf.Show.objects.all()})
                    

def export_act_techinfo(request, show_id):
    '''
    Export a csv of all act tech info details
    - includes only accepted acts
    - includes incomplete details
    - music sold separately
    '''

    reviewer = validate_perms(request, ('Tech Crew',))

 
    show = get_object_or_404(conf.Show, eventitem_id=show_id)
    show_booking = show.scheduler_events.first()
    location = show_booking.location
    acts = show_booking.get_acts(3)

    #build header, segmented in same structure as subclasses
    header =  ['Order','Act', 'Performer', 'Contact Email', 'Complete?', 'Rehearsal Time']
    header += ['Act Length', 'Intro Text', 'No Props', 'Preset Props',
               'Cued Props','Clear Props', 'Stage Notes']
    header += ['Track Title', 'Track Artist','Track', 'Track Length',
               'No Music', 'Need Mic', 'Use Own Mic','Audio Notes']
    header +=['Act Description','Costume Description']

    if location.describe == 'Theater':
        header += ['Cue #', 'Cue off of', 'Follow spot', 'Center Spot','Backlight', 'Cyc Light', 'Wash', 'Sound']
    else:
        header += ['Cue #', 'Cue off of', 'Follow spot', 'Wash', 'Sound']

    # now build content
    cues = conf.CueInfo.objects.filter(techinfo__act__in=acts)
    techinfo =[]
    for act in acts:
        # in case no ordering is set up.
        try:
            allocation = sched.ResourceAllocation.objects.get(event=show_booking,
                                                              resource__actresource___item=act)
            order = allocation.ordering.order
        except:
            order = 0
        
        rehearsals = ""
        for rehearsal in act.get_scheduled_rehearsals():
            rehearsals += str(rehearsal.start_time)+", "
            
        start = [order, act.title, act.performer,act.performer.contact.user_object.email,
                 act.tech.is_complete, rehearsals]
        start +=  act.tech.stage.dump_data
        start +=  act.tech.audio.dump_data
        start +=  act.tech.lighting.dump_data

        # one row per cue... for sortability
        for cue in cues.filter(techinfo__act=act).order_by('cue_sequence'):
            if location.describe == 'Theater':
                cue = [cue.cue_sequence, cue.cue_off_of, cue.follow_spot, cue.center_spot,
                          cue.backlight, cue.cyc_color, cue.wash, cue.sound_note]
            else:
                cue = [cue.cue_sequence, cue.cue_off_of, cue.follow_spot, cue.wash, cue.sound_note]

            techinfo.append(start+cue)


        # in case performers haven't done paperwork            
        if len(cues.filter(techinfo__act=act)) == 0:
            techinfo.append(start)

    # end for loop through acts
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s_acttect.csv' % show.title.replace(' ','_')
    writer = csv.writer(response)
    writer.writerow(header)
    for row in techinfo:
        writer.writerow(row)
    return response