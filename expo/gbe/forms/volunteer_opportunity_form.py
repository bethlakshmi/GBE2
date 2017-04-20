from django.forms import (
    ChoiceField,
    HiddenInput,
    IntegerField,
    ModelForm,
    ModelChoiceField,
)
from gbe.models import (
    AvailableInterest,
    GenericEvent,
    Room,
    VolunteerInterest,
)
from gbe.expoformfields import DurationFormField
from datetime import datetime, time
from django.utils.formats import date_format


time_start = 8 * 60
time_stop = 24 * 60
conference_times = [(time(mins / 60, mins % 60),
                     date_format(time(mins / 60, mins % 60),
                                 "TIME_FORMAT"))
                    for mins in range(time_start, time_stop, 30)]

class VolunteerOpportunityForm(ModelForm):
    day = ChoiceField(
        choices=['No Days Specified'],
        error_messages={'required': 'required'})
    time = ChoiceField(choices=conference_times)
    opp_event_id = IntegerField(widget=HiddenInput(),
                                      required=False)
    opp_sched_id = IntegerField(widget=HiddenInput(),
                                      required=False)
    num_volunteers = IntegerField(
        error_messages={'required': 'required'})
    location = ModelChoiceField(
        queryset=Room.objects.all(),
        error_messages={'required': 'required'})
    duration = DurationFormField(
        error_messages={'null': 'required'})
    volunteer_type = ModelChoiceField(
        queryset=AvailableInterest.objects.filter(visible=True),
        required=False)

    def __init__(self, *args, **kwargs):
        conference = kwargs.pop('e_conference')
        super(VolunteerOpportunityForm, self).__init__(*args, **kwargs)
        self.fields['day'] = ModelChoiceField(
            queryset=conference.conferenceday_set.all(),
            error_messages={'required': 'required'})

    def save(self, commit=True):
        data = self.cleaned_data
        event = super(VolunteerOpportunityForm, self).save(commit=False)
        day = data.get('day').day
        time_parts = map(int, data.get('time').split(":"))
        starttime = time(*time_parts)
        event.starttime = datetime.combine(day, starttime)
        super(VolunteerOpportunityForm, self).save(commit=commit)
        return event

    class Meta:
        model = GenericEvent
        fields = ['e_title',
                  'volunteer_type',
                  'num_volunteers',
                  'duration',
                  'day',
                  'time',
                  'location',
                  ]
        hidden_fields = ['opp_event_id']
