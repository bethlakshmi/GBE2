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
    (datetime(2015, 02, 19), 'Thursday'),
    (datetime(2015, 02, 20), 'Friday'),
    (datetime(2015, 02, 21), 'Saturday'),
    (datetime(2015, 02, 22), 'Sunday'),
)



time_start = 8 * 60
time_stop = 23 * 60 + 30
conference_times = [(time(mins/60, mins%60), str(mins/60) +":"+str(mins%60)  ) 
                    for mins in range (time_start, time_stop, 30)]



class EventScheduleForm(forms.Form):
    day = forms.ChoiceField(choices = conference_days)
    time = forms.ChoiceField(choices = conference_times)
    location = forms.ChoiceField(choices = [ (loc, loc.__str__()) for loc in LocationItem.objects.all()])
    duration = DurationFormField()




    
