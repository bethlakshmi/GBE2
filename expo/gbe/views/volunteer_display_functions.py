from gbe.forms import (
    VolunteerBidForm,
    VolunteerInterestForm,
    ParticipantForm
)
from django.forms import CharField


def get_volunteer_forms(volunteer):
    formset = []
    volunteerform = VolunteerBidForm(
        instance=volunteer,
        prefix='Volunteer Info',
        available_windows=volunteer.conference.windows(),
        unavailable_windows=volunteer.conference.windows())
    for interest in volunteer.volunteerinterest_set.filter(
        rank__gt=0).order_by(
            'interest__interest'):
        volunteerform.fields['interest_id-%s' % interest.pk] = CharField(
            max_length=200,
            help_text=interest.interest.help_text,
            label=interest.interest.interest,
            initial=interest.rank_description)
    formset += [volunteerform]
    formset += [ParticipantForm(
        instance=volunteer.profile,
        initial={'email': volunteer.profile.user_object.email,
                 'first_name': volunteer.profile.user_object.first_name,
                 'last_name': volunteer.profile.user_object.last_name},
        prefix='Contact Info')]
    return formset

def validate_interests(formset):
    valid_interests = True
    like_one_thing = False
    for interest_form in formset:
        # to avoid the hidden object hunt - the two points of difference
        # are the instance, and the initial value
        if interest_form.is_valid():
            if int(interest_form.cleaned_data.get('rank')) > 1:
                like_one_thing = True
        else:
            valid_interests = False
    return valid_interests, like_one_thing
