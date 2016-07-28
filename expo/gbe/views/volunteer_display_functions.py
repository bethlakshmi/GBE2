from gbe.forms import (
    VolunteerBidForm,
    VolunteerInterestForm,
    ParticipantForm
)


def get_volunteer_forms(volunteer):
    formset = []
    for interest in volunteer.volunteerinterest_set.all().order_by(
            'interest__interest'):
        formset += [VolunteerInterestForm(
            instance=interest,
            initial={'interest': interest.interest})]
    formset += [VolunteerBidForm(
        instance=volunteer,
        prefix='Volunteer Info',
        available_windows=volunteer.conference.windows(),
        unavailable_windows=volunteer.conference.windows())]
    formset += [ParticipantForm(
        instance=volunteer.profile,
        initial={'email': volunteer.profile.user_object.email,
                 'first_name': volunteer.profile.user_object.first_name,
                 'last_name': volunteer.profile.user_object.last_name},
        prefix='Contact Info')]
    return formset
