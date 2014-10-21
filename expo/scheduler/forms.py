from scheduler.models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
import datetime
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from gbe_forms_text import *
from gbe.expoformfields import DurationFormField

class EventsDisplayForm(forms.Form):
    event = forms.ChoiceField(choices= EventItem.objects.all(),
                              label='Event')
    location = forms.ChoiceField(choices=LocationItem.objects.all(),
                                 label = 'Location')
                                 
    class Meta:
        fields = ['event', 'location']

        



    
