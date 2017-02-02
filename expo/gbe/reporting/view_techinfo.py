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
    techinfo = export_techinfo(show_id, area=area)
    logger.info(techinfo)
    logger.info(techinfo[0])
    header = techinfo[0]

    return render(request,
                  'gbe/report/view_techinfo.tmpl',
                  {'this_show': show,
                   'acts': acts,
                   'area': area,
                   'all_shows': conf.Show.objects.filter(
                       conference=conference),
                   'techinfo': techinfo,
                   'colheaders': header,
                   'numheaders': len(header)
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'scheduling_link': scheduling_link,
                   'return_link': reverse('view_techinfo',
                                          urlconf='gbe.reporting.urls',)})

def export_techinfo(show_id, area='all'):
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
    header = ['Sort Order',
              'Order',
              'Act',
              'Performer',
              'Contact Email',
              'Complete?',
              'Rehearsal Time',
              'Act Length',
              ]
    header += ['Intro Text',
               'No Props',
               'Preset Props',
               'Cued Props',
               'Clear Props',
               'Stage Notes',
               'Need Mic',
               'Use Own Mic',
               ]
    header += ['Track Title',
               'Track Artist',
               'Track',
               'Track Length',
               'No Music',
               'Need Mic',
               'Use Own Mic',
               'Audio Notes',
               ]
    header += ['Cue #', 'Cue off of']
    header += ['Act Description',
               'Costume Description']
    if location.describe == 'Theater':
        header += ['Follow spot',
                   'Center Spot',
                   'Backlight',
                   'Cyc Light',
                   'Wash',
                   'Sound']
    else:
        header += ['Follow spot', 'Wash', 'Sound']

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
                             cue.sound_note,
                             ]
            else:
                cue_items = [cue.cue_sequence,
                             cue.cue_off_of,
                             cue.follow_spot,
                             cue.wash,
                             cue.sound_note,
                             ]
            start[0] = float("%d.%d" % (act.order, cue.cue_sequence))
            techinfo.append(start+cue_items)

        # in case performers haven't done paperwork
        if len(cues.filter(techinfo__act=act)) == 0:
            start[0] = act.order
            techinfo.append(start)

    # end for loop through acts
    cuesequenceindex = len(header) + 1

    # Winnow extraneous info by tech area
    if area is 'stage_mgmt':
        header = header
        newtechinfo = []
        for line in techinfo:
            line = line
            newtechinfo.append(line)
        techinfo = newtechinfo
    elif area is 'audio':
        header = header
        newtechinfo = []
        for line in techinfo:
            line = line
            newtechinfo.append(line)
        techinfo = newtechinfo
    elif area is 'lighting':
        header = header
        newtechinfo = []
        for line in techinfo:
            line = line
            newtechinfo.append(line)
        techinfo = newtechinfo

    return [header] + sorted(techinfo, key=lambda row: row[0])
