from django.forms import (
    ChoiceField,
    ModelForm,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import (
    Event,
    Room
)
from gbe.expoformfields import (
    DurationFormField,
)
from gbe.functions import get_current_conference
from datetime import time
from expo.settings import TIME_FORMAT


time_start = 8 * 60
time_stop = 24 * 60
conference_times = [(time(mins/60, mins % 60),
                     time(mins/60, mins % 60).strftime(TIME_FORMAT))
                    for mins in range(time_start, time_stop, 30)]


class ScheduleBasicForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    day = ChoiceField(choices=['No Days Specified'])
    time = ChoiceField(choices=conference_times)
    location = ModelChoiceField(
        queryset=Room.objects.all().order_by('name'))
    max_volunteer = IntegerField(required=True)

    class Meta:
        model = Event
        fields = ['e_title',
                  'e_description',
                  'duration',
                  'max_volunteer',
                  'day',
                  'time',
                  'location',
                  ]

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            conference = kwargs['instance'].e_conference
        else:
            conference = kwargs.pop('conference')
        super(ScheduleBasicForm, self).__init__(*args, **kwargs)
        self.fields['day'] = ModelChoiceField(
            queryset=conference.conferenceday_set.all())
