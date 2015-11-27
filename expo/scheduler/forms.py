from scheduler.models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from datetime import datetime, time
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from gbe_forms_text import *
from gbe.expoformfields import DurationFormField
import gbe.models as conf

conference_days = (
    (datetime(2016, 02, 4).strftime('%Y-%m-%d'), 'Thursday'),
    (datetime(2016, 02, 5).strftime('%Y-%m-%d'), 'Friday'),
    (datetime(2016, 02, 6).strftime('%Y-%m-%d'), 'Saturday'),
    (datetime(2016, 02, 7).strftime('%Y-%m-%d'), 'Sunday'),
)


time_start = 8 * 60
time_stop = 24 * 60

conference_times = [(time(mins/60, mins % 60),
                     time(mins/60, mins % 60).strftime("%I:%M %p"))
                    for mins in range(time_start, time_stop, 30)]


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
    actresource = forms.CharField(required=False, max_length=10,
                                  widget=forms.HiddenInput())


class WorkerAllocationForm (forms.Form):
    '''
    Form for selecting a worker to fill a slot in a Volunteer Opportunity
    '''
    worker = forms.ModelChoiceField(queryset=conf.Profile.objects.all(),
                                    required=False)
    role = forms.ChoiceField(choices=role_options, initial='Volunteer')
    label = forms.CharField(max_length=100, required=False)
    alloc_id = forms.IntegerField(required=False, widget=forms.HiddenInput())


class EventScheduleForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    
    day = forms.ChoiceField(choices=['No Days Specified'])
    time = forms.ChoiceField(choices=conference_times)
    location = forms.ChoiceField(choices=[
                (loc, loc.__str__()) for loc in
                LocationItem.objects.all().order_by('room__name')])
    duration = DurationFormField(
                   help_text=scheduling_help_texts['duration'])
    teacher = forms.ModelChoiceField(queryset=conf.Performer.objects.all(),
                                     required=False)
    moderator = forms.ModelChoiceField(queryset=conf.Persona.objects.all(),
                                       required=False)
    panelists = forms.ModelMultipleChoiceField(
        queryset=conf.Performer.objects.all(),
        required=False)
    staff_lead = forms.ModelChoiceField(queryset=conf.Profile.objects.all(),
                                        required=False)
    description = forms.CharField(required=False,
                                  widget=forms.Textarea,
                                  help_text=scheduling_help_texts
                                  ['description'])
    title = forms.CharField(required=False,
                            help_text=scheduling_help_texts['title'])


    def __init__(self, *args, **kwargs):
        conference = kwargs.pop('conference')
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
        starttime = time(*time_parts)
        event.starttime = datetime.combine(day, starttime)

        if commit:
            self.save()
        return event


class EventItemScheduleForm(forms.ModelForm):
    '''
    When we save an Event, we need to save changes to its duration
    '''
    duration = DurationFormField()

    class Meta:
        model = EventItem
