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
from django.contrib.auth.models import User, Group
from django.conf import settings
from gbetext import (
    acceptance_states,
    event_options,
    class_options,
)
from scheduler.models import Event as sEvent
from post_office import mail
from post_office.models import EmailTemplate
from django.conf import settings
import os
from django.contrib.sites.models import Site


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


def send_user_contact_email(name, from_address, message):
    subject = "EMAIL FROM GBE SITE USER %s" % name
    to_addresses = settings.USER_CONTACT_RECIPIENT_ADDRESSES
    mail.send(to_addresses,
              from_address,
              subject=subject,
              message=message,
              priority='now',
              )
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


def eligible_volunteers(event_start_time, event_end_time, conference):
    windows = []
    for window in conference.windows():
        if window.check_conflict(event_start_time, event_end_time):
            windows.append(window)

    return Volunteer.objects.filter(
        conference=conference).exclude(
        unavailable_windows__in=windows)


def get_or_create_template(name, base, subject):
    try:
        template = EmailTemplate.objects.get(name=name)
    except:
        with open(
            "%s/templates/gbe/email/%s.tmpl" % (
                os.path.dirname(__file__),
                base), "r") as textfile:
            textcontent = textfile.read()
        with open(
            "%s/templates/gbe/email/%s_html.tmpl" % (
                os.path.dirname(__file__),
                base), "r") as htmlfile:
            htmlcontent = htmlfile.read()
        template = EmailTemplate.objects.create(
            name=name,
            subject=subject,
            content=textcontent,
            html_content=htmlcontent,
            )
        template.save()


def send_bid_state_change_mail(bid_type, email, badge_name, status):
    name = '%s %s' % (bid_type, acceptance_states[status][1].lower())
    get_or_create_template(
        name,
        "default_bid_status_change",
        'Your %s proposal has changed status to %s' % (
                bid_type,
                acceptance_states[status][1]))
    site = Site.objects.get_current()
    mail.send(
        email,
        settings.DEFAULT_FROM_EMAIL,
        template=name,
        context={
            'name': badge_name,
            'bid_type': bid_type,
            'status': acceptance_states[status][1],
            'site': site.domain,
            'site_name': site.name},
        priority='now',
    )


def send_schedule_update_mail(participant_type, profile):
    name = '%s schedule update' % (participant_type.lower())
    get_or_create_template(
        name,
        "volunteer_schedule_update",
        "A change has been made to your %s Schedule!" % (
                participant_type))
    mail.send(
        profile.contact_email,
        settings.DEFAULT_FROM_EMAIL,
        template=name,
        context={
            'site': Site.objects.get_current().domain,
            'profile': profile},
        priority='now',
    )


def notify_reviewers_on_bid_change(bidder,
                                   bid_type,
                                   action,
                                   conference,
                                   group_name,
                                   review_url):
    name = '%s %s notification' % (bid_type.lower(), action.lower())
    get_or_create_template(
        name,
        "bid_submitted",
        "%s %s Occurred" % (bid_type, action))
    to_list = [user.email for user in
               User.objects.filter(groups__name=group_name)]
    mail.send(to_list,
              settings.DEFAULT_FROM_EMAIL,
              template=name,
              context = {
                'bidder': bidder,
                'bid_type': bid_type,
                'action': action,
                'conference': conference,
                'group_name': group_name,
                'review_url': Site.objects.get_current().domain+review_url},
              priority='now',
              )


def send_warnings_to_staff(bidder,
                           bid_type,
                           warnings):
    name = '%s schedule warning' % (bid_type.lower())
    get_or_create_template(
        name,
        "schedule_conflict",
        "URGENT: %s Schedule Conflict Occurred" % (bid_type))
    to_list = [user.email for user in
               User.objects.filter(groups__name='%s Coordinator' % bid_type)]
    for warning in warnings:
        if warning['email']:
            to_list += [warning['email']]
    
    mail.send(to_list,
              settings.DEFAULT_FROM_EMAIL,
              template=name,
              context = {
                'bidder': bidder,
                'bid_type': bid_type,
                'warnings': warnings},
              priority='now',
              )


def get_gbe_schedulable_items(confitem_type, filter_type=None, conference=None):
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
    confitems_list = confitem_class.objects.filter(conference=conference)

    if filter_type is not None:
        confitems_list = [
            confitem for confitem in confitems_list if
            confitem.sched_payload['details']['type'] == filter_type]

    return confitems_list
