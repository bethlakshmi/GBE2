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

conference_days = ( 
    (datetime(2015, 02, 19).strftime('%Y-%m-%d'), 'Thursday'),
    (datetime(2015, 02, 20).strftime('%Y-%m-%d'), 'Friday'),
    (datetime(2015, 02, 21).strftime('%Y-%m-%d'), 'Saturday'),
    (datetime(2015, 02, 22).strftime('%Y-%m-%d'), 'Sunday'),
)



time_start = 8 * 60
time_stop = 24 * 60  

conference_times = [(time(mins/60, mins%60), time(mins/60, mins%60).strftime("%I:%M %p")) 
                    for mins in range (time_start, time_stop, 30)]

class ActScheduleForm(forms.Form):
    '''
    Presents an act for scheduling as one line on a multi-line form. 
    '''
    performer = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))
    title = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}))


    show = forms.ModelChoiceField(queryset=Event.objects.all())
    order = forms.IntegerField()
    actresource = forms.CharField(required=False, max_length=10, widget=forms.HiddenInput())


class WorkerAllocationForm (forms.Form):
    '''
    Form for selecting a worker to fill a slot in a Volunteer Opportunity
    '''
    import gbe.models as conf
    worker = forms.ModelChoiceField(queryset = conf.Profile.objects.all())
    role = forms.ChoiceField(choices = role_options, initial='Volunteer')
    label = forms.CharField(max_length = 100, required=False)
    alloc_id = forms.IntegerField(required=False, widget = forms.HiddenInput())


class EventScheduleForm(forms.ModelForm):
    day = forms.ChoiceField(choices = conference_days)
    time = forms.ChoiceField(choices = conference_times)
    location = forms.ChoiceField(choices = [ (loc, loc.__str__()) for loc in LocationItem.objects.all()])
    duration = DurationFormField(help_text='Enter duration as HH:MM:SS')
    import gbe.models as conf
    teacher = forms.ModelChoiceField(queryset = conf.Performer.objects.all(), required = False)

    class Meta:
        model = Event
        fields = ['day', 'time', 'location', 'duration', 'max_volunteer', 'teacher']
        help_texts= {'duration':'Enter duration as HH:MM:SS'}
    def save(self, commit=True):
        data = self.cleaned_data
        event = super(EventScheduleForm, self).save(commit=False)
        day = data.get('day')
        time = data.get('time')
        day = ' '.join([day.split(' ')[0],time])
        
        event.starttime =datetime.strptime(day, "%Y-%m-%d %H:%M:%S")
        
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
