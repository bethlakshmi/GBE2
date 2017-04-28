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
from gbe.functions import get_current_conference
from gbe.forms.common_queries import (
    visible_profiles,
)
import pytz
from gbe.models import Show


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
