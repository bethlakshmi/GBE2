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
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User


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


def get_conf(biddable):
    conference = biddable.biddable_ptr.b_conference
    old_bid = conference.status == 'completed'
    return conference, old_bid


def get_current_conference():
    return Conference.current_conf()


def get_current_conference_slug():
    return Conference.current_conf().conference_slug


def get_conference_by_slug(slug):
    return Conference.by_slug(slug)


def get_conference_days(conference, open_to_public=None):
    if open_to_public is None or open_to_public is False:
        return conference.conferenceday_set.all()
    else:
        return conference.conferenceday_set.filter(
            open_to_public=True)


def get_conference_day(conference, date):
    return ConferenceDay.objects.get(conference=conference, day=date)


def conference_list():
    return Conference.objects.all()


def conference_slugs():
    return Conference.all_slugs()


def eligible_volunteers(event_start_time, event_end_time, conference):
    windows = []
    for window in conference.windows():
        if window.check_conflict(event_start_time, event_end_time):
            windows.append(window)

    return Volunteer.objects.filter(
        b_conference=conference).exclude(
        unavailable_windows__in=windows)


def get_gbe_schedulable_items(confitem_type,
                              filter_type=None,
                              conference=None):
    '''
    Queries the database for the conferece items relevant for each type
    and returns a queryset.
    '''
    if confitem_type in ['Panel', 'Movement', 'Lecture', 'Workshop']:
        filter_type, confitem_type = confitem_type, 'Class'
    elif confitem_type in ['Special Event',
                           'Volunteer Opportunity',
                           'Master Class',
                           'Drop-In Class']:
        filter_type, confitem_type = confitem_type, 'GenericEvent'

    if not conference:
        conference = Conference.current_conf()
    confitem_class = eval(confitem_type)
    confitems_list = confitem_class.objects.filter(e_conference=conference)

    if filter_type is not None:
        confitems_list = [
            confitem for confitem in confitems_list if
            confitem.sched_payload['details']['type'] == filter_type]

    return confitems_list
