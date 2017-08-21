import pytz
from datetime import datetime, time
from scheduler.data_transfer import Person
from django.contrib import messages
from gbe.models import UserMessage
from expo.settings import DATETIME_FORMAT


def get_single_role(data, roles=None):
    people = []
    if not roles:
        roles = [('teacher', 'Teacher'),
                 ('moderator', 'Moderator'),
                 ('staff_lead', 'Staff Lead')]
    for role_key, role in roles:
        if role_key in data:
            people += [Person(
                user=data[role_key].workeritem.as_subtype.user_object,
                public_id=data[role_key].workeritem.pk,
                role=role)]
    return people


def get_multi_role(data, roles=None):
    people = []
    if not roles:
        roles = [('panelists', 'Panelist')]
    for role_key, role in roles:
        if role_key in data and len(data[role_key]) > 0:
            for worker in data[role_key]:
                people += [Person(
                    user=worker.workeritem.as_subtype.user_object,
                    public_id=worker.workeritem.pk,
                    role=role)]
    return people


def get_start_time(data):
    day = data['day'].day
    time_parts = map(int, data['time'].split(":"))
    starttime = time(*time_parts, tzinfo=pytz.utc)
    return datetime.combine(day, starttime)

#
# Takes the HTTP Request from the view and builds the following user messages,
#   based upon the nature of the occurrence_response from scheduling:
#      - if there's a warning - user gets 1 warning colored msg per warning
#      - if there's an error - user gets 1 red error message per error
# These messages are not mutually exclusive.  Order of operation is most
#   severe (error) to least severe (success)
#
def show_general_status(request, status_response, view):
    for error in status_response.errors:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code=error.code,
                defaults={
                    'summary': error.code,
                    'description': error.code})
        messages.error(
            request,
            '%s  %s' % (user_message[0].description, error.details))

    for warning in status_response.warnings:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code=warning.code,
                defaults={
                    'summary': warning.code,
                    'description': warning.code})

        message_text = ''
        if warning.details:
            message_text += warning.details
        if warning.user:
            message_text += '<br>- Affected user: %s' % (
                warning.user.profile.display_name)
        if warning.occurrence:
            message_text += '<br>- Conflicting booking: %s, Start Time: %s' % (
                str(warning.occurrence),
                warning.occurrence.starttime.strftime(DATETIME_FORMAT))
        messages.warning(
            request,
            '%s  %s' % (user_message[0].description, message_text))


#
# Takes the HTTP Request from the view and builds the following user messages,
#   based upon the nature of the occurrence_response from scheduling:
#      - if there's an occurrence - user gets a green success
#      - sets warnings & errors (see show_general_status)
# These three messages are not mutually exclusive.  Order of operation is most
#   severe (error) to least severe (success)
#
def show_scheduling_occurrence_status(request, occurrence_response, view):
    show_general_status(request, occurrence_response, view)
    if occurrence_response.occurrence:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code="OCCURRENCE_UPDATE_SUCCESS",
                defaults={
                    'summary': "Occurrence has been updated",
                    'description': "Occurrence has been updated."})
        messages.success(
            request,
            '%s<br>- %s, Start Time: %s' % (
                user_message[0].description,
                str(occurrence_response.occurrence),
                occurrence_response.occurrence.starttime.strftime(
                    DATETIME_FORMAT)))

#
# Takes the HTTP Request from the view and builds the following user messages,
#   based upon the nature of the occurrence_response from scheduling:
#      - if there's a booking - user gets a green success
#      - sets warnings & errors (see show_general_status)
# These three messages are not mutually exclusive.  Order of operation is most
#   severe (error) to least severe (success)
#
def show_scheduling_booking_status(request, booking_response, view):
    show_general_status(request, booking_response, view)

    if booking_response.booking_id:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code="BOOKING_UPDATE_SUCCESS",
                defaults={
                    'summary': "User assignment has been updated.",
                    'description': "User has been assigned to event"})
        messages.success(
            request,
            user_message[0].description)
