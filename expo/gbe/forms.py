from gbe.models import *
from django import forms
from django.forms import ModelMultipleChoiceField
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
import datetime
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from gbe_forms_text import *
from expoformfields import DurationFormField
from scheduler.functions import set_time_format, conference_days, conference_times
from django.shortcuts import get_object_or_404



class ParticipantForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=True)

    how_heard = forms.MultipleChoiceField(choices=how_heard_options, 
                                          required=False,
                                          widget=forms.CheckboxSelectMultiple(),
                                          label=participant_labels['how_heard'])
    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = [ 'first_name', 'last_name', 'display_name', 'email', 
                   'address1', 'address2', 'city',
                   'state', 'zip_code', 'country', 'phone', 
                    'best_time', 'how_heard',
                  ]
        labels = participant_labels
        help_texts = participant_form_help_texts
        
    def save(self, commit=True):
        partform = super(ParticipantForm, self).save(commit=False)
        partform.user_object.email = self.cleaned_data['email']
        if len(self.cleaned_data['first_name'].strip()) > 0:
            partform.user_object.first_name = self.cleaned_data['first_name'].strip()
        if len(self.cleaned_data['last_name'].strip()) > 0:
            partform.user_object.last_name = self.cleaned_data['last_name'].strip()
        if self.cleaned_data['display_name']:
            pass   # if they enter a display name, respect it
        else:
            partform.display_name = " ".join ([self.cleaned_data['first_name'],
                                               self.cleaned_data['last_name']])
        if commit:
            partform.save()
            partform.user_object.save()
    
class ProfileAdminForm(ParticipantForm):
    '''
    Form for administratively modifying a Profile
    '''
    purchase_email = forms.CharField(required=True, label=participant_labels['purchase_email'])
    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = [ 'first_name', 'last_name', 'display_name', 'email', 'purchase_email',
                   'address1', 'address2', 'city',
                   'state', 'zip_code', 'country', 'phone', 
                    'best_time', 'how_heard'
                  ]
 


class UserCreateForm(UserCreationForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    username = forms.CharField(label=username_label, help_text=username_help)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = [ 'username', 'email', 'first_name', 'last_name',
                   'password1', 'password2']



class PersonaForm (forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Persona
        fields = [ 'name', 
                   'homepage', 
                   'bio', 
                   'experience',
                   'awards', 
                   'promo_image',
                   'performer_profile',
                   'contact'
        ]
        
        help_texts = persona_help_texts
        labels = persona_labels
        widgets = {'performer_profile': forms.HiddenInput(), 
                   'contact':forms.HiddenInput()}

class TroupeForm (forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Troupe
        fields= '__all__'
        help_texts = persona_help_texts
        labels = persona_labels

class ComboForm (forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Combo
        fields= ['contact', 'name', 'membership']

class ActEditForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(required=False, help_text = act_help_texts['act_duration'])
    track_duration = DurationFormField(required=False, help_text = act_help_texts['track_duration'],
                                       label = act_bid_labels['track_duration'])
    track_artist = forms.CharField(required=False)
    track_title = forms.CharField(required=False)
    shows_preferences = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                  choices=act_shows_options,
                                                  label=act_bid_labels['shows_preferences'],
                                                  help_text = act_help_texts['shows_preferences'])
    description = forms.CharField(required=True,
                                  label = act_bid_labels['description'],
                                  help_text = act_help_texts['description'],
                                  widget = forms.Textarea)

    class Meta:
        model = Act
        fields, required = Act().bid_fields
        fields += ['act_duration', 'track_duration', 'track_artist', 'track_title']
        labels = act_bid_labels
        help_texts=act_help_texts
  
class ActEditDraftForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(required=False, help_text = act_help_texts['act_duration'])
    track_duration = DurationFormField(required=False, help_text = act_help_texts['track_duration'],
                                       label = act_bid_labels['track_duration'])
    track_artist = forms.CharField(required=False)
    track_title = forms.CharField(required=False)
    shows_preferences = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                  choices=act_shows_options,
                                                  label=act_bid_labels['shows_preferences'],
                                                  help_text = act_help_texts['shows_preferences'],
                                                  required=False)
    class Meta:
        model = Act
        fields, required = Act().bid_fields
        fields += ['act_duration', 'track_duration', 'track_artist', 'track_title']
        required = Act().bid_draft_fields
        labels = act_bid_labels
        help_texts=act_help_texts

class ActTechInfoForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Act
        fields = '__all__'


 
class BidEvaluationForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = BidEvaluation
        fields = '__all__'
        widgets = {'evaluator': forms.HiddenInput(),
                   'bid': forms.HiddenInput()}

class BidStateChangeForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Biddable
        fields = ['accepted']
        required = ['accepted']
        labels = acceptance_labels
        help_texts = acceptance_help_texts

class EventCheckBox(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        time_format = set_time_format(days = 2)
        return str(obj) + " - " + obj.starttime.strftime(time_format)

class VolunteerBidStateChangeForm(BidStateChangeForm):
    from scheduler.models import Event
    events = EventCheckBox(queryset=Event.objects.filter(max_volunteer__gt=0).order_by('starttime'),
        	           widget=forms.CheckboxSelectMultiple(),
        	           required=False,
        	           label='Choose Volunteer Schedule')
    class Meta:
        model = Biddable
        fields = ['accepted', 'events']

    # the request is now available, add it to the instance data
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(VolunteerBidStateChangeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        from scheduler.models import Worker, ResourceAllocation, Event

        volform = super(VolunteerBidStateChangeForm, self).save(commit=False)
        time_format = set_time_format(days = 2)

        if commit:
            # Clear out previous assignments, deletes Worker and ResourceAllocation
            if not self.cleaned_data['accepted'] == 5:
              Worker.objects.filter(_item=volform.profile, role='Volunteer').delete()
 
            # if the act has been accepted, set the show.
            if self.cleaned_data['accepted'] == 3:
                worker = Worker(_item=volform.profile, role='Volunteer')
                worker.save()

                # Cast the act into the show by adding it to the schedule resource allocation
                for assigned_event in self.cleaned_data['events']:
                    event = get_object_or_404(Event, pk=assigned_event)
                    conflicts = worker._item.get_conflicts(event)
                    for problem in conflicts:
                        messages.warning(self.request, "Found event conflict, new booking " +str(event)
                                         + " - " + event.starttime.strftime(time_format) + " conflicts with "
                                         + str(problem) + " - " + problem.starttime.strftime(time_format))
                    volunteer_assignment = ResourceAllocation()
                    volunteer_assignment.event = event
                    volunteer_assignment.resource = worker
                    volunteer_assignment.save()
                    if event.extra_volunteers() > 0:
                        messages.warning(self.request, str(event) + " - " + event.starttime.strftime(time_format)+
                                         " is overfull.  Over by "+str(event.extra_volunteers())+" volunteer.")
            volform.save()
        return self




class ClassBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    schedule_constraints = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, 
                                                     choices = class_schedule_options,
                                                     label = classbid_labels['schedule_constraints'])
 

    class Meta:
        model = Class
        fields, required = Class().get_bid_fields
        help_texts = classbid_help_texts
        labels = classbid_labels

class ClassBidDraftForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    schedule_constraints = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, 
                                                     choices = class_schedule_options,
                                                     required = False,
                                                     label = classbid_labels['schedule_constraints'])
    ''' Needed this to override forced required value in Biddable.  Not sure why - it's
    allowed to be blank '''
    description = forms.CharField(required=False, 
                                  widget = forms.Textarea)

    class Meta:
        model = Class
        fields, requiredsubmit = Class().get_bid_fields
        required = Class().get_draft_fields
        help_texts = classbid_help_texts
        labels = classbid_labels


class VolunteerBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    title = forms.HiddenInput()
    description = forms.HiddenInput()                            
    availability = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, 
                                             choices = volunteer_availability_options,
                                             label = volunteer_labels['availability'],
                                             required = True)
    unavailability = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, 
                                             choices = volunteer_availability_options,
                                             label = volunteer_labels['unavailability'])

    interests = forms.MultipleChoiceField(widget= forms.CheckboxSelectMultiple, 
                                          choices = volunteer_interests_options)
    class Meta:
        model = Volunteer
        fields = '__all__'
        widgets = {'accepted': forms.HiddenInput(), 
                   'submitted' : forms.HiddenInput(),
                   'title' : forms.HiddenInput(), 
                   'description' : forms.HiddenInput(),
                   'profile' : forms.HiddenInput()}
        labels = volunteer_labels
        help_texts = volunteer_help_texts


class VolunteerOpportunityForm(forms.ModelForm):
    day = forms.ChoiceField(choices = conference_days)
    time = forms.ChoiceField(choices = conference_times)
    opp_event_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    opp_sched_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    num_volunteers = forms.IntegerField()
    location = forms.ModelChoiceField(queryset = Room.objects.all())
    class Meta:
        model = GenericEvent
        fields = ['title', 'num_volunteers', 'duration', 'day', 'time', 'location' ]
        hidden_fields = ['opp_event_id']


class VendorBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    description = forms.CharField(required=True, 
                                  widget = forms.Textarea,
                                  help_text = vendor_help_texts['description'],
                                  label = vendor_labels['description'])
    help_times = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple,
                                                choices = vendor_schedule_options,
                                                required=False,
                                                label = vendor_labels['help_times'])
  
    class Meta:
        model=Vendor
        fields = '__all__'
        help_texts = vendor_help_texts
        labels = vendor_labels
        widgets = {'accepted': forms.HiddenInput(), 
                   'submitted' : forms.HiddenInput(),
                   'profile' : forms.HiddenInput()}

class ActTechInfoForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Act
        fields = [ 'title','description','performer','video_link','video_choice']

class AudioInfoForm(forms.ModelForm):
    formtitle="Audio Info"
    class Meta:
        model=AudioInfo

class LightingInfoForm(forms.ModelForm):
    formtitle="Lighting Info"
    class Meta:
        model=LightingInfo


class StageInfoForm(forms.ModelForm):
    formtitle="Stage Info"
    class Meta:
        model=StageInfo

class ClassProposalForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    proposal = forms.CharField(max_length = 500,
                               widget = forms.Textarea,
                               help_text = class_proposal_help_texts['proposal'],
                               label = class_proposal_labels['proposal'])
    class Meta:
        model = ClassProposal
        fields = ['name', 'title', 'type', 'proposal']
        required = ['title']
        help_texts= class_proposal_help_texts
        labels = class_proposal_labels

class ProposalPublishForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    proposal = forms.CharField(max_length = 500,
                               widget = forms.Textarea,
                               help_text = class_proposal_help_texts['proposal'],
                               label = class_proposal_labels['proposal'])
    class Meta:
        model = ClassProposal
        fields = ['title', 'type', 'proposal', 'name', 'display']
        help_texts= proposal_edit_help_texts
        labels = proposal_edit_labels	
        
class ConferenceVolunteerForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = ConferenceVolunteer
        fields, required = ConferenceVolunteer().bid_fields
        widgets = {'bid': forms.HiddenInput()}


class ProfilePreferencesForm(forms.ModelForm):
    inform_about=forms.MultipleChoiceField(choices=inform_about_options,
                                           required=False,
                                           widget=forms.CheckboxSelectMultiple(),
                                           label=profile_preferences_labels['inform_about'])
    class Meta:
        model = ProfilePreferences
        fields = ['inform_about', 'in_hotel', 'show_hotel_infobox']
        help_texts = profile_preferences_help_texts
        labels = profile_preferences_labels
