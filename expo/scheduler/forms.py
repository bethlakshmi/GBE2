from scheduler.models import *
from django import forms
from datetime import datetime, time
from django.utils.timezone import utc
from gbe_forms_text import *
from gbe.expoformfields import DurationFormField
from gbe.functions import get_current_conference
from gbe.forms.common_queries import (
    visible_personas,
    visible_profiles,
)
import pytz
from gbe.models import Show
from gbe.scheduling.forms.schedule_selection_form import conference_times


class ActScheduleForm(forms.Form):
    '''
    Presents an act for scheduling as one line on a multi-line form.
    '''
    performer = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    title = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    show = forms.ModelChoiceField(queryset=Event.objects.all())
    order = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(ActScheduleForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            conf_shows = Show.objects.filter(
                e_conference=initial['show'].eventitem.get_conference())
            self.fields['show'].queryset = Event.objects.filter(
                eventitem__in=conf_shows)


class WorkerAllocationForm (forms.Form):
    '''
    Form for selecting a worker to fill a slot in a Volunteer Opportunity
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    worker = forms.ModelChoiceField(
        queryset=visible_profiles,
        required=False)
    role = forms.ChoiceField(choices=role_options, initial='Volunteer')
    label = forms.CharField(max_length=100, required=False)
    alloc_id = forms.IntegerField(required=False, widget=forms.HiddenInput())


class EventItemScheduleForm(forms.ModelForm):
    '''
    When we save an Event, we need to save changes to its duration
    '''
    duration = DurationFormField()

    class Meta:
        model = EventItem
        fields = '__all__'


# DEPRECATED - remove after refactor done
class EventScheduleForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    day = forms.ChoiceField(choices=['No Days Specified'])
    time = forms.ChoiceField(choices=conference_times)
    location = forms.ModelChoiceField(
            queryset=LocationItem.objects.all().order_by('room__name'))
    duration = DurationFormField(
                   help_text=scheduling_help_texts['duration'])
    teacher = forms.ModelChoiceField(queryset=visible_personas,
                                     required=False)
    moderator = forms.ModelChoiceField(queryset=visible_personas,
                                       required=False)
    panelists = forms.ModelMultipleChoiceField(
        queryset=visible_personas,
        required=False)
    staff_lead = forms.ModelChoiceField(queryset=visible_profiles,
                                        required=False)
    description = forms.CharField(required=False,
                                  widget=forms.Textarea,
                                  help_text=scheduling_help_texts
                                  ['description'])
    title = forms.CharField(required=False,
                            help_text=scheduling_help_texts['title'])

    def __init__(self, *args, **kwargs):
        conference = get_current_conference()
        super(EventScheduleForm, self).__init__(*args, **kwargs)
        self.fields['day'] = forms.ModelChoiceField(
            queryset=conference.conferenceday_set.all())

    class Meta:
        model = Event
        fields = ['day',
                  'time',
                  'location',
                  'duration',
                  'max_volunteer',
                  'teacher',
                  'moderator',
                  'panelists',
                  'staff_lead',
                  'description']
        help_texts = scheduling_help_texts

    def save(self, commit=True):
        data = self.cleaned_data
        event = super(EventScheduleForm, self).save(commit=False)
        day = data.get('day').day
        time_parts = map(int, data.get('time').split(":"))
        starttime = time(*time_parts, tzinfo=pytz.utc)
        event.starttime = datetime.combine(day, starttime)

        if commit:
            self.save()
        return event
