from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from scheduler.forms import EventScheduleForm
from scheduler.views.functions import (
    get_event_display_info,
    set_single_role,
    set_multi_role,
)
from scheduler.models import (
    EventItem,
    LocationItem,
)
from django.views.decorators.cache import never_cache
from django.utils.formats import date_format
from gbe.functions import get_conference_by_slug
from scheduler.functions import (
    cal_times_for_conf,
    event_info,
)
import gbe.models as conf
from expo.settings import (
    DATE_FORMAT,
    TIME_FORMAT,
    SITE_URL,
    )
from gbe.functions import get_conference_by_slug

@login_required
@never_cache
def export_calendar(request,
                    conference=None,
                    cal_format='gbook',
                    event_types='All',
                    day=None,
):
    '''
    View to export calendars, .  
    Used to allow importing of the calendar information into other
    applications, such as Guidebook.

    conference  - Slug for the conference we want to export data for
    cal_format  - Which format to use for the exported data, can be 'gbook'
                  for Guidebook csv, 'ical' for iCal calendar programs (ics)
    event_types - Which event types to include, usually will be 'All' to
                  generate a complete calendar, but could also be 'Class',
                  'Show', etc, or a list or tuple of event_types
    day         - Which day of the conference to get calendar info for,
                  None or 'All' gets info for entire conference
    '''
    #  TODO: Add ability to filter on a users schedule for things like
    #  volunteer shifts.

    if conference == None:
        conference = conf.Conference.current_conf()
    else:
        conference = get_conference_by_slug(conference)
    if day == 'All':
        day == None
    cal_times=cal_times_for_conf(conference, day)

    local_domain = SITE_URL.split('://')[1].replace('www.', '')
    if event_types == 'All':
        event_types = ['Show',
                       'Class',
                       'Special Event',
                       'Master Class',
                       'Drop-In Class']
    elif event_types == 'Show':
        event_types == ['Show',
                        'Special Event',
                        'Master Class',
                        'Drop-In Class',
                        ]
    elif type(event_types) != type([]) or type(event_types) != type(()):
        event_types = [event_types]
    events = []
    for event_type in event_types:
        events = events + event_info(confitem_type=event_type,
                                     cal_times=cal_times,
                                     conference=conference)
    return_file = ''
    if cal_format == 'gbook':
        return_file = return_file + \
                      "'Session Title','Date','Time Start','Time End',"+ \
                      "'Room/Location','Schedule Track (Optional)',"+ \
                      "'Description (Optional)',''\r\n"
        for event in events:
            return_file = return_file+"'%s'," % (event['title'])
            return_file = return_file+"'%s'," % \
                         (date_format(event['start_time'], 'DATE_FORMAT'))
            return_file = return_file+"'%s'," % \
                         (date_format(event['start_time'], 'TIME_FORMAT'))
            return_file = return_file+"'%s'," % \
                         (date_format(event['stop_time'], 'TIME_FORMAT'))
            return_file = return_file+"'%s'," % (event['location'])
            return_file = return_file+"'%s'," % (event['type'].split('.')[0])
            return_file = return_file+"'%s'," % \
                          (event['description'].replace('\n', '') \
                           .replace('\r', ''))
            return_file = return_file+"'%s%s'\r\n" % (SITE_URL, event['link'])

    if cal_format == 'ical':
        return_file=return_file+'''
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Great Burlesque Exposition//GBE2 Scheduler//EN
'''
        for event in events:
            return_file=return_file+'BEGIN:VEVENT\n'
            return_file=return_file+'UID:%s-%s-%s@%s\n' \
                         % (conference.conference_slug,
                            event['title'].replace(' ', ''),
                            event['start_time'].strftime('%F-%R'),
                            local_domain,
                            )
            return_file=return_file+'DTSTAMP:%s\n' % \
                         (event['start_time'].strftime('%Y%m%dT%H%M%SZ'))
            return_file=return_file+'TZID:%s\n' % \
                         (event['start_time'].strftime('%Z'))
            return_file=return_file+'DTSTART:%s\n' % \
                         (date_format(event['start_time'], 'DATETIME_FORMAT'))
            return_file=return_file+'DTEND:%s\n' % \
                         (date_format(event['stop_time'], 'DATETIME_FORMAT'))
            return_file=return_file+'SUMMARY:%s\n' % \
                         (event['title'])
            return_file=return_file+'URL:%s%s\n' % (SITE_URL, event['link'])
            return_file=return_file+'END:VEVENT\n'
        return_file=return_file+'END:VCALENDAR\n'

    return HttpResponse(return_file, content_type='text/csv')
