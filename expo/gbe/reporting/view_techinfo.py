# View functions for reporting
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.management import call_command
from django.views.decorators.cache import never_cache

import gbe.models as conf
import scheduler.models as sched
import ticketing.models as tix
from gbe.ticketing_idd_interface import (
    get_checklist_items,
    get_checklist_items_for_tickets
    )

import os
import csv
from reportlab.pdfgen import canvas

from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from expo.gbe_logging import logger


@never_cache
def view_techinfo(request):
    '''
    Show the list of act tech info for all acts in a given show for a given
    tech area.
    export specifies the type of export, csv or view.  area is the tech area
    of the information being exported, audio, lighting, stage_mgmt, or all.
    '''

    validate_perms(request, ('Tech Crew',))
    # using try not get_or_404 to cover the case where the show is there
    # but does not have any scheduled events.
    # I can still show a list of shows this way.

    scheduling_link = ''

    area = request.GET.get('area', 'all')
    show = None
    acts = []
    show_id = request.GET.get('show_id', None)
    area = request.GET.get('area', 'all')

    if show_id == None:
        logger.error('view_techinfo: Invalid show_id: %s' % (show_id))
        pass

    show = conf.Show.objects.get(eventitem_id=show_id)
    acts = show.scheduler_events.first().get_acts(status=3)
    acts = sorted(acts, key=lambda act: act.order)
    if validate_perms(
            request, ('Scheduling Mavens',), require=False):
        scheduling_link = reverse(
            'schedule_acts',
            urlconf='scheduler.urls',
            args=[show.pk])

    if show:
        conference = show.conference
    else:
        conf_slug = request.GET.get('conf_slug', None)
        conference = get_conference_by_slug(conf_slug)

    logger.info(area+', '+show_id)
    header, techinfo = build_techinfo(show_id, area=area)
    logger.info(techinfo)
    logger.info(techinfo[0])

    return render(request,
                  'gbe/report/view_techinfo.tmpl',
                  {'this_show': show,
                   'area': area,
                   'all_shows': conf.Show.objects.filter(
                       conference=conference),
                   'techinfo': techinfo,
                   'header': header,
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'scheduling_link': scheduling_link,
                   'return_link': reverse('view_techinfo',
                                          urlconf='gbe.reporting.urls',)})

def build_techinfo(show_id, area='all'):
    '''
    Export a list of act tech info details
    - includes only accepted acts
    - includes incomplete details
    - music sold separately
    area is 'all' for all details available,
        'audio' is for audio details only,
        'lighting' is for only lighting details,
        'stage_mgmt' is for only stage management details (props, mic, etc)
    '''
    # Move this into a function file?  It is not a view.

    show = get_object_or_404(conf.Show, eventitem_id=show_id)
    show_booking = show.scheduler_events.first()
    location = show_booking.location
    acts = show_booking.get_acts(3)

    # build header, segmented in same structure as subclasses
    header = ['Order',
              'Act',
              'Performer',
              'Act Length',]

    if area in ('all', 'stage_mgmt'):
        header += [
            'Intro Text',
            'Rehearsal Time',
            'Preset Props',
            'Cued Props',
            'Clear Props',
            'Stage Notes',
            'Need Mic',
            'Use Own Mic',]
    
    if area in ('all', 'audio'):
        header += [
            'Track',
            'Track Artist',
            'Track Length',
            'No Music',
            'Audio Notes',]
    if area in ('audio',):
        header += [
            'Need Mic',
            'Use Own Mic',]

    if area in ('all', 'lighting'):
        header += [
            'Act Description',
            'Costume Description',
            'Cue #',
            'Cue off of',
            'Follow spot',]
        if location.describe == 'Theater':
            header += [
                'Center Spot',
                'Backlight',
                'Cyc Light',]
        header += [
            'Wash',
            'Sound',]

    # now build content
    cues = conf.CueInfo.objects.filter(techinfo__act__in=acts)
    techinfo = []
    for act in acts:
        tech_row = [
            act.order,
            act.title,
            ("Person", act.performer, act.performer.contact.user_object.email),
        ]
        stage_info = act.tech.stage.dump_data
        audio_info= act.tech.audio.dump_data
        tech_row += [stage_info[0],]

        if area in ('all', 'stage_mgmt'):
            rehearsals = ""
            for rehearsal in act.get_scheduled_rehearsals():
                rehearsals += str(rehearsal.start_time)+", "
            tech_row += [
                stage_info[1],
                rehearsals,
                stage_info[3],
                stage_info[4],
                stage_info[5],
                stage_info[6],
                audio_info[4],
                audio_info[5],
             ]

        if area in ('all', 'audio'):
            tech_row += [
                ("File", audio_info[0], audio_info[2]),
                audio_info[1],
                audio_info[3],
                audio_info[6],
                audio_info[7],
            ]
        if area in ('audio'):
            tech_row += [
                audio_info[4],
                audio_info[5],
             ]

        if area in ('all', 'lighting'):
            tech_row += act.tech.lighting.dump_data
            cue_sequence = []
            cue_off_of = []
            follow_spot = []
            wash = []
            sound_note = []
            if location.describe == 'Theater':
                center_spot = []
                backlight = []
                cyc_color = []

            for cue in cues.filter(techinfo__act=act).order_by('cue_sequence'):
                cue_sequence += [cue.cue_sequence]
                cue_off_of += [cue.cue_off_of]
                follow_spot += [cue.follow_spot]
                if location.describe == 'Theater':
                    center_spot += [cue.center_spot]
                    backlight += [cue.backlight]
                    cyc_color += [cue.cyc_color]
                wash += [cue.wash]
                sound_note += [cue.sound_note]

            tech_row += [cue_sequence, cue_off_of, follow_spot]
            if location.describe == 'Theater':
                tech_row += [center_spot, backlight, cyc_color]
            tech_row += [wash, sound_note]

        techinfo.append(tech_row)

    return (
        header,
        sorted(techinfo, key=lambda row: row[0]))
