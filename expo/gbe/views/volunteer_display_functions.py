from gbe.forms import (
    VolunteerBidForm,
    VolunteerInterestForm,
    ParticipantForm
)
from django.forms import (
    CharField,
    ModelMultipleChoiceField,
    MultipleChoiceField,
)
from gbe_forms_text import (
    how_heard_options,
    participant_labels,
    volunteer_help_texts,
    volunteer_labels
)
from gbetext import (
    states_options,
)


def get_volunteer_forms(volunteer):
    formset = []
    volunteerform = VolunteerBidForm(
        instance=volunteer,
        prefix='Volunteer Info',
        available_windows=volunteer.conference.windows(),
        unavailable_windows=volunteer.conference.windows())
    volunteerform.fields['available_windows'] = ModelMultipleChoiceField(
        queryset=volunteer.available_windows.all(),
        label=volunteer_labels['availability'],
        help_text=volunteer_help_texts['volunteer_availability_options'],
        required=True)
    volunteerform.fields['unavailable_windows'] = ModelMultipleChoiceField(
        queryset=volunteer.unavailable_windows.all(),
        label=volunteer_labels['unavailability'],
        help_text=volunteer_help_texts['volunteer_availability_options'],
        required=True)
    for interest in volunteer.volunteerinterest_set.filter(
        rank__gt=0).order_by(
            'interest__interest'):
        volunteerform.fields['interest_id-%s' % interest.pk] = CharField(
            max_length=200,
            help_text=interest.interest.help_text,
            label=interest.interest.interest,
            initial=interest.rank_description)
    participantform = ParticipantForm(
        instance=volunteer.profile,
        initial={'email': volunteer.profile.user_object.email,
                 'first_name': volunteer.profile.user_object.first_name,
                 'last_name': volunteer.profile.user_object.last_name},
        prefix='Contact Info')

    participantform.fields['state'] = MultipleChoiceField(
        choices=[(volunteer.profile.state,
                  dict(states_options)[volunteer.profile.state])],
    )
    how_heard_selected = []
    for option in how_heard_options:
        if option[0] in volunteer.profile.how_heard:
            how_heard_selected += [option]
    participantform.fields['how_heard'] = MultipleChoiceField(
        choices=how_heard_selected,
        required=False,
        label=participant_labels['how_heard'])
    return [volunteerform, participantform]


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
