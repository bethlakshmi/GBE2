from gbe.models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
import datetime
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from gbe_forms_text import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [ 'display_name',
                   'purchase_email', 'address1', 'address2', 'city', 'state', 'zip_code',
                   'country', 'onsite_phone', 'best_time', 'how_heard', 
                  ]

class ParticipantForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    onsite_phone = forms.CharField(required=True)
    how_heard = forms.MultipleChoiceField(choices=how_heard_options, 
                                          required=False,
                                           widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = [ 'first_name', 'last_name', 'email', 'display_name',
                   'address1', 'address2', 'city',
                   'state', 'zip_code', 'country', 'onsite_phone', 'offsite_preferred',
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

    

class BidderInfoForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True,
          help_text=bidder_info_phone_error)

    class Meta:
        model = Profile
        fields = [ 'onsite_phone', 'email']


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
                   'video_link',
                   'puffsheet', 
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

class ActBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    help_texts=act_help_texts
    class Meta:
        model = Act
        fields, required = Act().bid_fields
    def save (self, *args, **kwargs):
        return super(ActBidForm, self).save(*args, **kwargs)

class ActEditForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    help_texts=act_help_texts
    class Meta:
        model = Act
        fields, required = Act().bid_fields

class ActDraftForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    help_texts=act_help_texts
    class Meta:
        model = Act
        fields = '__all__'

class ActSubmitForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    help_texts=act_help_texts
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



class ClassBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Class
        fields, required = Class().get_bid_fields
#    def save(self, *args, **kwargs):
#        return super(ClassBidForm, self).save(*args, **kwargs)

class ClassEditForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Class
        fields = '__all__'

class VolunteerBidForm(forms.ModelForm):
    title = forms.HiddenInput()
    description = forms.HiddenInput()                            
    availability = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, 
                                             choices = volunteer_availability_options)
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

class VendorBidForm(forms.ModelForm):
    help_times = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple,
                                                choices = vendor_schedule_options)
    class Meta:
        model=Vendor
        fields = '__all__'
        labels = vendor_labels
        widgets = {'accepted': forms.HiddenInput(), 
                   'submitted' : forms.HiddenInput(),
                   'profile' : forms.HiddenInput()}


class AudioInfoForm(forms.ModelForm):
    formtitle="Audio Info"
    class Meta:
        model=AudioInfo


class AudioInfoBidForm(forms.ModelForm):
    formtitle="Audio Info"
    class Meta:
        model=AudioInfo
        fields=['title','artist']

        
        labels= audioinfo_labels

class LightingInfoForm(forms.ModelForm):
    formtitle="Lighting Info"
    class Meta:
        model=LightingInfo


class PropsInfoForm(forms.ModelForm):
    formtitle="Props Info"
    class Meta:
        model=PropsInfo


class LightingInfoBidForm(forms.ModelForm):
    formtitle="Lighting Info"
    class Meta:
        model=LightingInfo
        fields = []
        

class PropsInfoBidForm(forms.ModelForm):
    formtitle="Props Info"
    class Meta:
        model=PropsInfo
        fields=[]


class ClassProposalForm(forms.ModelForm):
    class Meta:
        model = ClassProposal
        fields = '__all__'
        required = ['title']
        help_texts= class_proposal_help_texts
        
class ProfilePreferencesForm(forms.ModelForm):
    inform_about=forms.MultipleChoiceField(choices=inform_about_options,
                                           required=False,
                                           widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = ProfilePreferences
        fields = ['inform_about', 'in_hotel']
        help_texts = profile_preferences_help_texts
