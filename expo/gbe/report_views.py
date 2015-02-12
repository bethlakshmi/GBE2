# View functions for reporting
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404

import gbe.models as conf
import scheduler.models as sched
import ticketing.models as tix

import csv
from reportlab.pdfgen import canvas
from gbe.functions import *

def review_staff_area(request):
    '''
      Shows listing of staff area stuff for drill down
    '''
    header = ['Area','Leaders','Check Staffing']
    try:
        areas = conf.GenericEvent.objects.filter(type='Staff Area', visible=True)
    except:
        areas = []
        
    return render (request, 'gbe/report/staff_areas.tmpl',
                  {'header': header, 'areas': areas})


def staff_area(request, area_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled, volunteers scheduled, 
    sorted by time/day
    See ticket #250
    '''
    try:
        area = conf.GenericEvent.get(eventitem_id=area_id)
    except:
        area = get_object_or_404(conf.Show, eventitem_id=area_id)
    sched_event = sched.Event.objects.filter(eventitem=area)
    opps = []
    for event in sched_event:
        opps += event.get_volunteer_opps('Volunteer')    
    
    return render (request, 'gbe/report/staff_area_schedule.tmpl',
                  {'opps': opps, 'area': area})

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
        acts = show.scheduler_events.first().get_acts(3)

    except:
        show = None
        acts = []
    
    return render (request, 'gbe/report/act_tech_review.tmpl',
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


def room_schedule(request, room_id=None):
    if room_id:
        rooms=[get_object_or_404(sched.LocationItem, resourceitem_id=room_id)]
    else:
        try:
            rooms=sched.LocationItem.objects.all()
        except:
            rooms=[]
    
    # rearrange the data into the format of:
    #  - room & date of booking
    #       - list of bookings
    # this lets us have 1 table per day per room
    room_set = []
    for room in rooms:
        day_events = []
        current_day = None
        for booking in room.get_bookings:
            if not current_day:
                current_day = booking.start_time.date()
            if current_day != booking.start_time.date():
                room_set += [{'room': room,
                             'date': current_day,
                             'bookings': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            day_events += [booking]
                
        
    
    return render (request, 'gbe/report/room_schedule.tmpl',
                  {'room_date': room_set})


def room_setup(request):
    try:
        rooms=sched.LocationItem.objects.all()
    except:
        rooms=[]
    
    # rearrange the data into the format of:
    #  - room & date of booking
    #       - list of bookings
    # this lets us have 1 table per day per room
    room_set = []
    for room in rooms:
        day_events = []
        current_day = None
        for booking in room.get_bookings:
            booking_class = sched.EventItem.objects.get_subclass(eventitem_id=booking.eventitem.eventitem_id)

            if not current_day:
                current_day = booking.start_time.date()
            if current_day != booking.start_time.date():
                if len(day_events) > 0:
                    room_set += [{'room': room,
                             'date': current_day,
                             'bookings': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            if booking_class.__class__.__name__ == 'Class':
                day_events += [{'event':booking,
                                'class':booking_class}]
                
        
    
    return render (request, 'gbe/report/room_setup.tmpl',
                  {'room_date': room_set})
