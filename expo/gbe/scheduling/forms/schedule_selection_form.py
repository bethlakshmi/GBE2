from django.forms import (
    CharField,
    ChoiceField,
    ModelForm,
    IntegerField,
    ModelChoiceField,
    ModelMultipleChoiceField,
    Textarea,
)
from gbe.models import (
    Event,
    Room
)
from gbe.expoformfields import (
    DurationFormField,
)
from gbe.functions import get_current_conference
from django.utils.formats import date_format
from datetime import datetime, time
import pytz
from gbe_forms_text import (
    scheduling_help_texts,
    scheduling_labels,
)
from gbe.forms.common_queries import (
    visible_personas,
    visible_profiles,
)


time_start = 8 * 60
time_stop = 24 * 60
conference_times = [(time(mins/60, mins % 60),
                     date_format(time(mins/60, mins % 60), "TIME_FORMAT"))
                    for mins in range(time_start, time_stop, 30)]


class ScheduleSelectionForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    day = ChoiceField(choices=['No Days Specified'])
    time = ChoiceField(choices=conference_times)
    location = ModelChoiceField(
        queryset=Room.objects.all().order_by('name'))
    duration = DurationFormField(
        help_text=scheduling_help_texts['duration'])
    max_volunteer = IntegerField(required=False)
    teacher = ModelChoiceField(
        queryset=visible_personas,
        required=False)
    moderator = ModelChoiceField(
        queryset=visible_personas,
        required=False)
    panelists = ModelMultipleChoiceField(
        queryset=visible_personas,
        required=False)
    staff_lead = ModelChoiceField(
        queryset=visible_profiles,
        required=False)

    class Meta:
        model = Event
        fields = ['e_title', 'e_description']
        help_texts = scheduling_help_texts
        labels = scheduling_labels


    def __init__(self, *args, **kwargs):
        conference = get_current_conference()
        super(ScheduleSelectionForm, self).__init__(*args, **kwargs)
        self.fields['day'] = ModelChoiceField(
            queryset=conference.conferenceday_set.all())

    def save(self, commit=True):
        data = self.cleaned_data
        event = super(ScheduleSelectionForm, self).save(commit=False)
        day = data.get('day').day
        time_parts = map(int, data.get('time').split(":"))
        starttime = time(*time_parts, tzinfo=pytz.utc)
        event.starttime = datetime.combine(day, starttime)

        if commit:
            self.save()
        return event
