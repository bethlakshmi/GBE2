import pytz
from datetime import datetime, timedelta
import gbe.models as conf
from django.http import Http404
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.conf import settings
from gbetext import (
    event_options,
    class_options,
)
from gbe.duration import DateTimeRange
from scheduler.models import Event as sEvent


def validate_profile(request, require=False):
    '''
    Return the user profile if any
    '''
    if request.user.is_authenticated():
        try:
            return request.user.profile
        except conf.Profile.DoesNotExist:
            if require:
                raise Http404
    else:
        return None


def validate_perms(request, perms, require=True):
    '''
    Validate that the requesting user has the stated permissions
    Returns profile object if perms exist, False if not
    '''
    profile = validate_profile(request, require=False)
    if not profile:
        if require:
            raise PermissionDenied
        else:
            return False
    if perms == 'any':
        if len(profile.privilege_groups) > 0:
            return profile
        else:
            if require:
                raise PermissionDenied
            else:
                return False
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    if require:                # error out if permission is required
        raise PermissionDenied
    return False               # or just return false if we're just checking


def mail_to_group(subject, message, group_name):
    '''
    Sends mail to a privilege group, designed for use by bid functions
    Will always send using default_from_email

    '''
    to_list = [user.email for user in
               User.objects.filter(groups__name=group_name)]
    if not settings.DEBUG:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, to_list)
    return None


def send_user_contact_email(name, from_address, message):
    subject = "EMAIL FROM GBE SITE USER %s" % name
    to_addresses = settings.USER_CONTACT_RECIPIENT_ADDRESSES
    send_mail(subject,
              message,
              from_address,
              to_addresses)
    # TO DO: handle (log) possible exceptions
    # TO DO: log usage of this function
    # TO DO: close the spam hole that this opens up.


def get_conf(biddable):
    conference = biddable.biddable_ptr.b_conference
    old_bid = conference.status == 'completed'
    return conference, old_bid


def get_current_conference():
    return conf.Conference.current_conf()


def get_conference_by_slug(slug):
    return conf.Conference.by_slug(slug)


def get_conference_days(conference):
    return conference.conferenceday_set.all()


def get_conference_day(conference, date):
    return conf.ConferenceDay.objects.get(conference=conference, day=date)


def conference_list():
    return conf.Conference.objects.all()


def conference_slugs():
    return conf.Conference.all_slugs()


def get_events_list_by_type(event_type, conference):
    event_type = event_type.lower()
    items = []
    if event_type == "all":
        return conf.Event.get_all_events(conference)

    event_types = dict(event_options)
    class_types = dict(class_options)
    if event_type in map(lambda x: x.lower(), event_types.keys()):
        items = conf.GenericEvent.objects.filter(
            type__iexact=event_type,
            visible=True,
            e_conference=conference).order_by('title')
    elif event_type in map(lambda x: x.lower, class_types.keys()):
        items = conf.Class.objects.filter(
            accepted='3',
            visible=True,
            type__iexact=event_type,
            e_conference=conference).order_by('title')
    elif event_type == 'show':
        items = conf.Show.objects.filter(
            e_conference=conference).order_by('title')
    elif event_type == 'class':
        items = conf.Class.objects.filter(
            accepted='3',
            visible=True,
            e_conference=conference).exclude(
                type='Panel').order_by('title')
    else:
        items = []
    return items


def available_volunteers(event_start_time):
    one_minute = timedelta(0, 60)
    tz = pytz.utc
    event_start_time = event_start_time + one_minute
    windows = []
    conference = get_current_conference()
    for window in conference.windows():
        starttime = tz.localize(datetime.combine(window.day.day, window.start))
        endtime = tz.localize(datetime.combine(window.day.day, window.end))
        window_range = DateTimeRange(starttime=starttime,
                                     endtime=endtime)
        if event_start_time in window_range:
            windows.append(window)
    return conf.Volunteer.objects.filter(available_windows__in=windows)
