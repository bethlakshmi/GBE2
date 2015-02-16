# View functions for reporting
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q

import gbe.models as conf
import scheduler.models as sched
import ticketing.models as tix

import csv
from reportlab.pdfgen import canvas
from gbe.functions import *

def list_reports(request):
    '''
      Shows listing of all reports in this area
    '''
    viewer_profile = validate_profile(request, require=True)
    if viewer_profile.user_object.is_staff:
        return render (request, 'gbe/report/report_list.tmpl')
    else:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))



def review_staff_area(request):
    '''
      Shows listing of staff area stuff for drill down
    '''
    viewer_profile = validate_profile(request, require=True)
    if not viewer_profile.user_object.is_staff:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

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
    viewer_profile = validate_profile(request, require=True)
    if not viewer_profile.user_object.is_staff:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    area = get_object_or_404(sched.EventItem, eventitem_id=area_id)
    sched_event = sched.Event.objects.filter(eventitem=area).order_by('starttime')
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
    reviewer = validate_perms(request, ('Registrar',))

    people = conf.Profile.objects.all()
    acts = conf.Act.objects.filter(accepted=3)
    tickets = tix.Transaction.objects.exclude(ticket_item__ticket_style=u'')
    roles = sched.Worker.objects.all()
    commits = sched.ResourceAllocation.objects.all()

    header=['Badge Name', 'First', 'Last', 'Tickets', 'Personae', 'Staff Lead',
            'Volunteering', 'Presenter', 'Show']

    person_details = []
    for person in people:
        ticket_list = ""
        staff_lead_list = ""
        volunteer_list = ""
        class_list = ""
        personae_list = ""
        show_list = ""

        for ticket in tickets.filter(purchaser__matched_to_user=person.user_object):
            ticket_list += ticket.ticket_item.ticket_style+", "
            
        for lead in roles.filter(role="Staff Lead", _item=person):
            for commit in commits.filter(resource=lead):
                staff_lead_list += str(commit.event.eventitem)+', '
            
        for volunteer in roles.filter(role="Volunteer", _item=person):
            for commit in commits.filter(resource=volunteer):
                volunteer_list += str(commit.event.eventitem)+', '
                
        for performer in person.get_performers():
            personae_list += str(performer) + ', '
            for teacher in roles.filter((Q(role="Teacher") |
                                         Q(role="Moderator") |
                                         Q(role="Panelist"))
                                        & Q(_item=performer)):
                for commit in commits.filter(resource=teacher):
                    class_list += teacher.role +': '+str(commit.event.eventitem)+', '
            for act in acts.filter(performer=performer):
                for commit in commits.filter(resource__actresource___item=act):
                    show_list += str(commit.event.eventitem)+', '

        
        person_details.append([person.get_badge_name(), person.user_object.first_name,
                               person.user_object.last_name, ticket_list, personae_list,
                               staff_lead_list, volunteer_list, class_list, show_list])
    
 
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=print_badges.csv' 
    writer = csv.writer(response)
    writer.writerow(header)
    for row in person_details:
        writer.writerow(row)
    return response

def personal_schedule(request, profile_id='All'):
    viewer_profile = validate_profile(request, require=True)
    if not viewer_profile.user_object.is_staff:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    if profile_id == 'All':
        people = conf.Profile.objects.all().select_related()
    else:
        people =[]
        
    return render (request, 'gbe/report/printable_schedules.tmpl',
                  {'people': people})
 

 
def review_act_techinfo(request, show_id=1):
    '''
    Show the list of act tech info for all acts in a given show 
    '''
    reviewer = validate_perms(request, ('Tech Crew',))
    
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.  I can still show a list of shows this way.
    try:
        show = conf.Show.objects.get(eventitem_id=show_id)
        acts = show.scheduler_events.first().get_acts(status=3)
        acts = sorted(acts, key=lambda act: act.order)
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
    header =  ['Sort Order', 'Order','Act', 'Performer', 'Contact Email', 'Complete?', 'Rehearsal Time']
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
        rehearsals = ""
        for rehearsal in act.get_scheduled_rehearsals():
            rehearsals += str(rehearsal.start_time)+", "
            
        start = [act.order, act.title, act.performer,act.performer.contact.user_object.email,
                 act.tech.is_complete, rehearsals]
        start +=  act.tech.stage.dump_data
        start +=  act.tech.audio.dump_data
        start +=  act.tech.lighting.dump_data

        # one row per cue... for sortability
        start.insert(0, '')
        for cue in cues.filter(techinfo__act=act).order_by('cue_sequence'):
            
            if location.describe == 'Theater':
                cue_items = [cue.cue_sequence, cue.cue_off_of, cue.follow_spot, cue.center_spot,
                          cue.backlight, cue.cyc_color, cue.wash, cue.sound_note]
            else:
                cue_items = [cue.cue_sequence, cue.cue_off_of, cue.follow_spot, cue.wash, cue.sound_note]
            start[0] =  float("%d.%d" % (act.order, cue.cue_sequence))
            techinfo.append(start+cue_items)


        # in case performers haven't done paperwork            
        if len(cues.filter(techinfo__act=act)) == 0:
            start[0]= act.order
            techinfo.append(start)

    # end for loop through acts
    cuesequenceindex = 24 # magic number, obtained by counting headers
    
    techinfo = sorted(techinfo, key=lambda row:row[0]) 
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s_acttect.csv' % show.title.replace(' ','_')
    writer = csv.writer(response)
    writer.writerow(header)
    for row in techinfo:
        writer.writerow(row)
    return response


def room_schedule(request, room_id=None):
    viewer_profile = validate_profile(request, require=True)
    if not viewer_profile.user_object.is_staff:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

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
    viewer_profile = validate_profile(request, require=True)
    if not viewer_profile.user_object.is_staff:
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

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

def export_badge_report(request):
    '''
    Export a csv of all act tech info details
    - includes only accepted acts
    - includes incomplete details
    - music sold separately
    '''

    reviewer = validate_perms(request, ('Registrar',))

    people = conf.Profile.objects.all()
    badges = tix.Transaction.objects.filter(ticket_item__badgeable=True).order_by('ticket_item')

    #build header, segmented in same structure as subclasses
    header =  ['First','Last', 'username', 'Badge Name', 'Badge Type', 'Date', 'State' ]

    badge_info = []
    # now build content - the order of loops is specific here, we need ALL transactions,
    #  if they are limbo, then the purchaser should have a BPT first/last name
    for badge in badges:
        
        try:
            for person in people.filter(user_object=badge.purchaser.matched_to_user):
                badge_info.append([badge.purchaser.first_name, badge.purchaser.last_name,
                           person.user_object.username, person.get_badge_name(), badge.ticket_item.title, badge.import_date, 'In GBE'])
            if len(people.filter(user_object=badge.purchaser.matched_to_user)) == 0:
                badge_info.append([badge.purchaser.first_name, badge.purchaser.last_name,
                                    badge.purchaser.matched_to_user, badge.purchaser.first_name,
                                    badge.ticket_item.title, badge.import_date, 'No Profile'])
        except:
        
            # if no profile, use purchase info from BPT
            badge_info.append([badge.purchaser.first_name, badge.purchaser.last_name,
                                    badge.purchaser.email, badge.purchaser.first_name,
                                    badge.ticket_item.title, badge.import_date, 'No User'])
            

    # end for loop through acts
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=print_badges.csv' 
    writer = csv.writer(response)
    writer.writerow(header)
    for row in badge_info:
        writer.writerow(row)
    return response
