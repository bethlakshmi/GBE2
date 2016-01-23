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

from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from expo.gbe_logging import logger


def list_reports(request):
    '''
      Shows listing of all reports in this area
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    else:
        conference = get_current_conference()
    return render(request,
                  'gbe/report/report_list.tmpl', {
                      'conference_slugs': conference_slugs(),
                      'conference': conference,
                      'return_link': reverse('report_list',
                                             urlconf='gbe.report_urls')})


def review_staff_area(request):
    '''
      Shows listing of staff area stuff for drill down
    '''
    viewer_profile = validate_perms(request, 'any', require=True)

    conference_slugs = conf.Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = conf.Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = conf.Conference.current_conf()

    header = ['Area', 'Leaders', 'Check Staffing']
    try:
        areas = conf.GenericEvent.objects.filter(type='Staff Area',
                                                 visible=True).filter(
                                                     conference=conference)
        shows = conf.Show.objects.all()
    except:
        areas = []
        shows = []

    return render(request, 'gbe/report/staff_areas.tmpl',
                  {'header': header,
                   'areas': areas,
                   'shows': shows,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


def staff_area(request, area_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, 'any', require=True)

    conference_slugs = conf.Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = conf.Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = conf.Conference.current_conf()

    area = get_object_or_404(sched.EventItem, eventitem_id=area_id)
    sched_event = sched.Event.objects.filter(
        eventitem=area).order_by('starttime').filter(conference=conference)
    opps = []
    for event in sched_event:
        opps += event.get_volunteer_opps('Volunteer').filter(conference=conference)
    return render(request, 'gbe/report/staff_area_schedule.tmpl',
                  {'opps': opps,
                   'area': area,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


def env_stuff(request, conference_choice=None):
    '''
    Generates an envelope-stuffing report.
    '''
    reviewer = validate_perms(request, ('Registrar',))

    if conference_choice:
        conference = get_conference_by_slug(conference_choice)
    else:
        conference = get_current_conference()

    people = conf.Profile.objects.all()
    acts = conf.Act.objects.filter(accepted=3, conference=conference)
    tickets = tix.Transaction.objects.filter(
        ticket_item__bpt_event__conference=conference)
    roles = sched.Worker.objects.filter(
        Q(allocations__event__eventitem__event__conference=conference))
    commits = sched.ResourceAllocation.objects.filter(
        Q(event__eventitem__event__conference=conference))

    header = ['Badge Name',
              'First',
              'Last',
              'Tickets',
              'Ticket format',
              'Personae',
              'Staff Lead',
              'Volunteering',
              'Presenter',
              'Show']

    person_details = []
    for person in people:
        ticket_list = ""
        staff_lead_list = ""
        volunteer_list = ""
        class_list = ""
        personae_list = ""
        show_list = ""
        ticket_names = ""

        for ticket in tickets.filter(
                purchaser__matched_to_user=person.user_object):
            ticket_list += str(ticket.ticket_item.bpt_event.ticket_style)+", "
            ticket_names += ticket.ticket_item.title+", "

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
                                         Q(role="Panelist")) &
                                        Q(_item=performer)):
                for commit in commits.filter(resource=teacher):
                    class_list += (teacher.role +
                                   ': ' +
                                   str(commit.event.eventitem) +
                                   ', ')
            for act in acts.filter(performer=performer):
                for commit in commits.filter(resource__actresource___item=act):
                    show_list += str(commit.event.eventitem)+', '

        person_details.append(
            [person.get_badge_name().encode('utf-8').strip(),
             person.user_object.first_name.encode('utf-8').strip(),
             person.user_object.last_name.encode('utf-8').strip(),
             ticket_names, ticket_list,
             personae_list,
             staff_lead_list,
             volunteer_list,
             class_list,
             show_list])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=env_stuff.csv'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in person_details:
        writer.writerow(row)
    return response


def personal_schedule(request, profile_id='All'):
    viewer_profile = validate_perms(request, 'any', require=True)

    conference_slugs = conf.Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = conf.Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = conf.Conference.current_conf()

    if profile_id == 'All':
        people = conf.Profile.objects.all().select_related()
    else:
        people = []  # Set it to be self, in list format

    tmp_people = []
    for person in people:
        for tmp_event in person.schedule:
            if conference.conference_slug == tmp_event.eventitem.get_conference().conference_slug:
                tmp_people.append(person)
                break  # Yes, I know this is bad form, refactor later

    return render(request,
                  'gbe/report/printable_schedules.tmpl',
                  {'people': tmp_people,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


def review_act_techinfo(request, show_id=None):
    '''
    Show the list of act tech info for all acts in a given show
    '''
    validate_perms(request, ('Tech Crew',))
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.
    # I can still show a list of shows this way.

    show = None
    acts = []

    if show_id:
        try:
            show = conf.Show.objects.get(eventitem_id=show_id)
            acts = show.scheduler_events.first().get_acts(status=3)
            acts = sorted(acts, key=lambda act: act.order)
        except:
            logger.error("review_act_techinfo: Invalid show id")
            pass
    if show:
        conference = show.conference
    else:
        conf_slug = request.GET.get('conf_slug', None)
        conference = get_conference_by_slug(conf_slug)
    return render(request,
                  'gbe/report/act_tech_review.tmpl',
                  {'this_show': show,
                   'acts': acts,
                   'all_shows': conf.Show.objects.filter(
                       conference=conference),
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'return_link': reverse('act_techinfo_review',
                                          urlconf='gbe.report_urls')})


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

    # build header, segmented in same structure as subclasses
    header = ['Sort Order',
              'Order',
              'Act',
              'Performer',
              'Contact Email',
              'Complete?',
              'Rehearsal Time']
    header += ['Act Length',
               'Intro Text',
               'No Props',
               'Preset Props',
               'Cued Props',
               'Clear Props',
               'Stage Notes']
    header += ['Track Title',
               'Track Artist',
               'Track',
               'Track Length',
               'No Music',
               'Need Mic',
               'Use Own Mic',
               'Audio Notes']
    header += ['Act Description',
               'Costume Description']

    if location.describe == 'Theater':
        header += ['Cue #',
                   'Cue off of',
                   'Follow spot',
                   'Center Spot',
                   'Backlight',
                   'Cyc Light',
                   'Wash',
                   'Sound']
    else:
        header += ['Cue #', 'Cue off of', 'Follow spot', 'Wash', 'Sound']

    # now build content
    cues = conf.CueInfo.objects.filter(techinfo__act__in=acts)
    techinfo = []
    for act in acts:
        rehearsals = ""
        for rehearsal in act.get_scheduled_rehearsals():
            rehearsals += str(rehearsal.start_time)+", "

        start = [act.order,
                 act.title,
                 act.performer,
                 act.performer.contact.user_object.email,
                 act.tech.is_complete,
                 rehearsals]
        start += act.tech.stage.dump_data
        start += act.tech.audio.dump_data
        start += act.tech.lighting.dump_data

        # one row per cue... for sortability
        start.insert(0, '')
        for cue in cues.filter(techinfo__act=act).order_by('cue_sequence'):

            if location.describe == 'Theater':
                cue_items = [cue.cue_sequence,
                             cue.cue_off_of,
                             cue.follow_spot,
                             cue.center_spot,
                             cue.backlight,
                             cue.cyc_color,
                             cue.wash,
                             cue.sound_note]
            else:
                cue_items = [cue.cue_sequence,
                             cue.cue_off_of,
                             cue.follow_spot,
                             cue.wash,
                             cue.sound_note]
            start[0] = float("%d.%d" % (act.order, cue.cue_sequence))
            techinfo.append(start+cue_items)

        # in case performers haven't done paperwork
        if len(cues.filter(techinfo__act=act)) == 0:
            start[0] = act.order
            techinfo.append(start)

    # end for loop through acts
    cuesequenceindex = 24  # magic number, obtained by counting headers

    techinfo = sorted(techinfo, key=lambda row: row[0])
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s_acttech.csv' \
        % show.title.replace(' ', '_')
    writer = csv.writer(response)
    writer.writerow(header)
    for row in techinfo:
        writer.writerow(row)
    return response


def room_schedule(request, room_id=None):
    viewer_profile = validate_perms(request,
                                    'any',
                                    require=True)

    conference_slugs = conf.Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = conf.Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = conf.Conference.current_conf()

    if room_id:
        rooms = [get_object_or_404(sched.LocationItem,
                                   resourceitem_id=room_id)]
    else:
        try:
            rooms = sched.LocationItem.objects.all()
        except:
            rooms = []

    conf_days = conference.conferenceday_set.all()
    tmp_days = []
    for position in range(0, len(conf_days)):
        tmp_days.append(conf_days[position].day)
    conf_days = tmp_days

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
                
                if current_day in conf_days:
                    room_set += [{'room': room,
                                  'date': current_day,
                                  'bookings': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            day_events += [booking]
        if current_day in conf_days:
            room_set += [{'room': room,
                          'date': current_day,
                          'bookings': day_events}]
    return render(request, 'gbe/report/room_schedule.tmpl',
                  {'room_date': room_set,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


def room_setup(request):

    conference_slugs = conf.Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = conf.Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = conf.Conference.current_conf()

    conf_days = conference.conferenceday_set.all()
    tmp_days = []
    for position in range(0, len(conf_days)):
        tmp_days.append(conf_days[position].day)
    conf_days = tmp_days

    viewer_profile = validate_perms(request, 'any', require=True)

    try:
        rooms = sched.LocationItem.objects.all()
    except:
        rooms = []

    # rearrange the data into the format of:
    #  - room & date of booking
    #       - list of bookings
    # this lets us have 1 table per day per room
    room_set = []
    for room in rooms:
        day_events = []
        current_day = None
        for booking in room.get_bookings:
            booking_class = sched.EventItem.objects.get_subclass(
                eventitem_id=booking.eventitem.eventitem_id)

            if not current_day:
                current_day = booking.start_time.date()
            if current_day != booking.start_time.date():
                if (current_day in conf_days and len(day_events) > 0):
                    room_set += [{'room': room,
                                  'date': current_day,
                                  'bookings': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            if booking_class.__class__.__name__ == 'Class':
                day_events += [{'event': booking,
                                'class': booking_class}]
        if (current_day in conf_days and len(day_events) > 0):
            room_set += [{'room': room,
                          'date': current_day,
                          'bookings': day_events}]

    return render(request,
                  'gbe/report/room_setup.tmpl',
                  {'room_date': room_set,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


def export_badge_report(request, conference_choice=None):
    '''
    Export a csv of all badge printing details.
    '''
    reviewer = validate_perms(request, ('Registrar',))

    people = conf.Profile.objects.all()

    if conference_choice:
        badges = tix.Transaction.objects.filter(
            ticket_item__bpt_event__badgeable=True,
            ticket_item__bpt_event__conference__conference_slug=conference_choice).order_by(
                'ticket_item')

    else:
        badges = tix.Transaction.objects.filter(
            ticket_item__bpt_event__badgeable=True).exclude(
                ticket_item__bpt_event__conference__status='completed').order_by(
                    'ticket_item')

    # build header, segmented in same structure as subclasses
    header = ['First',
              'Last',
              'username',
              'Badge Name',
              'Badge Type',
              'Date',
              'State']

    badge_info = []
    # now build content - the order of loops is specific here,
    # we need ALL transactions, if they are limbo, then the purchaser
    # should have a BPT first/last name
    for badge in badges:
        try:
            for person in people.filter(
                    user_object=badge.purchaser.matched_to_user):
                badge_info.append(
                    [badge.purchaser.first_name.encode('utf-8').strip(),
                     badge.purchaser.last_name.encode('utf-8').strip(),
                     person.user_object.username,
                     person.get_badge_name().encode('utf-8').strip(),
                     badge.ticket_item.title,
                     badge.import_date,
                     'In GBE'])
            if len(people.filter(
                    user_object=badge.purchaser.matched_to_user)) == 0:
                badge_info.append(
                    [badge.purchaser.first_name.encode('utf-8').strip(),
                     badge.purchaser.last_name.encode('utf-8').strip(),
                     badge.purchaser.matched_to_user,
                     badge.purchaser.first_name.encode('utf-8').strip(),
                     badge.ticket_item.title,
                     badge.import_date,
                     'No Profile'])
        except:

            # if no profile, use purchase info from BPT
            badge_info.append(
                [badge.purchaser.first_name.encode('utf-8').strip(),
                 badge.purchaser.last_name.encode('utf-8').strip(),
                 badge.purchaser.email,
                 badge.purchaser.first_name.encode('utf-8').strip(),
                 badge.ticket_item.title,
                 badge.import_date,
                 'No User'])

    # end for loop through acts
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=print_badges.csv'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in badge_info:
        writer.writerow(row)
    return response
