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

class ScheduleEvent(forms.ModelForm):

    required_css_class = 'required'
    error_css_class = 'error'
#    start_time = 
    location = models.CharField(max_length=64)
    parent_event = models.CharField(max_length = 128)

    def conflict(check_time, check_item, parent_event, item_type = 'Location'):
        '''
    Check event tree for a conflict of check_item at check_time.  Returns True if check_item
    is scheduled at check_time.  Uses parent_event to enter tree at a known location.
        '''

    
