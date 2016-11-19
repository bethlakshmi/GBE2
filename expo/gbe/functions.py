from gbe.models import (
    Class,
    Conference,
    ConferenceDay,
    Event,
    GenericEvent,
    Profile,
    Show,
    Volunteer,
)
from django.http import Http404
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.conf import settings
from gbetext import (
    event_options,
    class_options,
)
from scheduler.models import Event as sEvent


def validate_profile(request, require=False):
    '''
    Return the user profile if any
    '''
    if request.user.is_authenticated():
        try:
            return request.user.profile
        except Profile.DoesNotExist:
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
    conference = biddable.biddable_ptr.conference
    old_bid = conference.status == 'completed'
    return conference, old_bid


def get_current_conference():
    return Conference.current_conf()


def get_conference_by_slug(slug):
    return Conference.by_slug(slug)


def get_conference_days(conference):
    return conference.conferenceday_set.all()


def get_conference_day(conference, date):
    return ConferenceDay.objects.get(conference=conference, day=date)


def conference_list():
    return Conference.objects.all()


def conference_slugs():
    return Conference.all_slugs()


def get_events_list_by_type(event_type, conference):
    event_type = event_type.lower()
    items = []
    if event_type == "all":
        return Event.get_all_events(conference)

    event_types = dict(event_options)
    class_types = dict(class_options)
    if event_type in map(lambda x: x.lower(), event_types.keys()):
        items = GenericEvent.objects.filter(
            type__iexact=event_type,
            visible=True,
            conference=conference).order_by('title')
    elif event_type in map(lambda x: x.lower, class_types.keys()):
        items = Class.objects.filter(
            accepted='3',
            visible=True,
            type__iexact=event_type,
            conference=conference).order_by('title')
    elif event_type == 'show':
        items = Show.objects.filter(
            conference=conference).order_by('title')
    elif event_type == 'class':
        items = Class.objects.filter(
            accepted='3',
            visible=True,
            conference=conference).exclude(
                type='Panel').order_by('title')
    else:
        items = []
    return items


'''
#  eligible = not unavailable.  VolunteerBid lets the user select available
#     and unavailable times.  Eligible volunteers have said they were
#     unavailable in the volunteer time window(s) that correspond to this
#     event AND bid their time for this conference.
'''
def eligible_volunteers(event_start_time, event_end_time, conference):
    windows = []
    for window in conference.windows():
        if window.check_conflict(event_start_time, event_end_time):
            windows.append(window)

    return Volunteer.objects.filter(
        conference=conference).exclude(
        unavailable_windows__in=windows)


def show_potential_workers(category, start_time, end_time, conference):
    '''
    Get lists of potential workers for this opportunity.
      - interested_volunteers - rated the interest above "neither interested
         or disinterested"
      - available_volunteers - have the time available
      - all_volunteers - everyone who offered ... ever
    '''
    eligible = eligible_volunteers(start_time, end_time, conference)
    return {'interested_volunteers': eligible,
            'all_volunteers': eligible,
            'available_volunteers': eligible}
