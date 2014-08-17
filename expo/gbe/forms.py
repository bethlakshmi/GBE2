from gbe.models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
import datetime
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from gbe_forms_text import *
from expoformfields import DurationFormField

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
                    'best_time', 'how_heard'
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
    bid_reviews = forms.MultipleChoiceField(choices=bid_review_options, required=False)
    def save(self, commit=True):
        form = super(ProfileAdminForm, self).save(commit=False)
        form.bid_reviewer=",".join(self.cleaned_data('bid_reviewer'))
        if commit:
            form.save()

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
                   'festivals',
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


class BidEvaluationForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = BidEvaluation
        fields = '__all__'
        widgets = {'evaluator': forms.HiddenInput(),
                   'bid': forms.HiddenInput()}



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
    title = forms.HiddenInput()
    description = forms.HiddenInput()                            
    availability = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, 
                                             choices = volunteer_availability_options,
                                             label = volunteer_labels['availability'])
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
    class Meta:
        model = ClassProposal
        fields = '__all__'
        required = ['title']
        help_texts= class_proposal_help_texts
        
class ProfilePreferencesForm(forms.ModelForm):
    inform_about=forms.MultipleChoiceField(choices=inform_about_options,
                                           required=False,
                                           widget=forms.CheckboxSelectMultiple(),
                                           label=profile_preferences_labels['inform_about'])
    class Meta:
        model = ProfilePreferences
        fields = ['inform_about', 'in_hotel']
        help_texts = profile_preferences_help_texts
        labels = profile_preferences_labels
