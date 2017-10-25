from django.forms import (
    ChoiceField,
    FloatField,
    Form,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import (
    Room
)
from gbe.functions import get_current_conference
from django.utils.formats import date_format
from datetime import time
from gbe_forms_text import schedule_occurrence_labels

time_start = 8 * 60
time_stop = 24 * 60
conference_times = [(time(mins/60, mins % 60),
                     date_format(time(mins/60, mins % 60), "TIME_FORMAT"))
                    for mins in range(time_start, time_stop, 30)]


class ScheduleOccurrenceForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    day = ChoiceField(choices=['No Days Specified'], required=True)
    time = ChoiceField(choices=conference_times, required=True)
    duration = FloatField(min_value=0.5,
                          max_value=12,
                          required=True,
                          label=schedule_occurrence_labels['duration'])
    location = ModelChoiceField(
        queryset=Room.objects.all().order_by('name'))
    max_volunteer = IntegerField(required=True, initial=0)


    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            conference = kwargs['instance'].e_conference
        else:
            conference = kwargs.pop('conference')
        super(ScheduleOccurrenceForm, self).__init__(*args, **kwargs)
        self.fields['day'] = ModelChoiceField(
            queryset=conference.conferenceday_set.all(),
            empty_label=None)
