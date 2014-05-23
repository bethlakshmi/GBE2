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
                   'country', 'onsite_phone', 'best_time', 'how_heard', 'preferred_contact'
                  ]

class ParticipantForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = [ 'first_name', 'last_name', 'email', 'display_name',
                   'address1', 'address2', 'city',
                   'state', 'zip_code', 'country', 'onsite_phone', 'offsite_preferred',
                   'preferred_contact', 'best_time', 'how_heard'
                  ]
        labels = participant_labels
        help_texts = participant_form_help_texts

    # overload save to make sure there is always a display name
    def save(self, commit=True):
      partform = super(ParticipantForm, self).save(commit=False)
      partform.user_object.email = self.cleaned_data['email']
      partform.user_object.first_name = self.cleaned_data['first_name']
      partform.user_object.last_name = self.cleaned_data['last_name']
      if self.cleaned_data['display_name']:
          pass   # if they enter a display name, respect it
      else:
        partform.display_name = self.cleaned_data['first_name']+" "+self.cleaned_data['last_name']
      if commit:
         partform.save()
         partform.user_object.save()
         
    def clean(self):
      super(ParticipantForm, self).clean()
      contact = self.cleaned_data.get('preferred_contact')
      onsite = self.cleaned_data.get('onsite_phone')
      offsite = self.cleaned_data.get('offsite_preferred')
      if contact == 'Phone call' or contact == 'Text':
        if onsite == '' and offsite == '':
          self._errors['onsite_phone']=self.error_class([phone_error1])
          self._errors['offsite_preferred']=self.error_class([phone_error2])
          self._errors['preferred_contact']=self.error_class([phone_error3])
          raise forms.ValidationError(phone_validation_error_text)
      return self.cleaned_data


    
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


class RegistrationForm(UserCreationForm):
    '''
    Form for creating a GBE user. Collects info for User object as
    well as for user's profile (Participant object)
    '''
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model=User
        fields = ['username', 'first_name','last_name',
                  'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserCreateForm(UserCreationForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = [ "username", "email", 'first_name', 'last_name',
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
    performer_profile = forms.widgets.HiddenInput()
    class Meta:
        model = Persona
        fields = [ 'name', 
                   'homepage', 
                   'contact',
                   'bio', 
                   'experience',
                   'awards', 
                   'promo_image',
                   'video_link',
                   'puffsheet', 
                   'festivals',
                   'performer_profile'
        ]
        
        help_texts = persona_help_texts
        labels = persona_labels

class PersonaEditForm(forms.ModelForm):
    class Meta:
        model=Persona


class TroupeForm (forms.ModelForm):
    class Meta:
        model = Troupe
        fields='__all__'

class ComboForm (forms.ModelForm):
    class Meta:
        model = Combo
        fields= ['contact', 'name', 'membership']


class ActForm (forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    duration = forms.CharField(max_length=128)
#    duration = forms.TimeField(input_formats=['%H:%M:%S', '%H:%M'])
    class Meta:
        model = Act
        fields = [ 'title', 
                   'description', 
                   'performer', 
                   'intro_text', ]

class ActBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Act
        fields, required = Act().bid_fields
    def save (self, *args, **kwargs):
        return super(ActBidForm, self).save(*args, **kwargs)


class ActEditForm(forms.ModelForm):
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
        fields = [ 'vote',
                   'notes' ]
    def save (self, *args, **kwargs):
        return super(BidEvaluationForm, self).save(*args, **kwargs)
   
class ClassBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Class
        fields, required = Class().get_bid_fields
    def save(self, *args, **kwargs):
        return super(ClassBidForm, self).save(*args, **kwargs)

class ClassEditForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    class Meta:
        model = Class
        field = '__all__'

class VendorBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    
    # Needed information about Bidder
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True, 
          help_text=bidder_info_phone_error)
    address1 = forms.CharField(max_length=128, required=False)
    address2 = forms.CharField(max_length=128, required=False)
    city = forms.CharField(max_length=128, required=False)
    prof_state = forms.ChoiceField(required=False, choices=states_options, label="State" )
    zip_code = forms.IntegerField(required=False)
    country = forms.CharField(required=False)
    offsite_preferred = forms.CharField( label="Business Phone:", required=False,
          help_text=offsite_vendor_help_text )
	# Forced required when in submission (not draft)
    company = forms.CharField(required=True, label='Company Name' )
    description = forms.CharField(widget=forms.Textarea, required=True, 
    					label='Business Description', 
                        help_text=vendor_description_help_text )
    class Meta:
        model = VendorBid
        fields = [ 'vend_time',  'company', 'first_name', 'last_name', 
        			'address1', 'address2', 'city', 'prof_state', 'zip_code',  
        			'country', 'onsite_phone', 'offsite_preferred', 'email',  
        			'description', 'website', 'logo', 'want_help', 
        			'Saturday_9AM_to_12PM', 'Saturday_12PM_to_4PM',
        			'Saturday_4PM_to_8PM', 'Saturday_after_8PM', 
        			'Sunday_9AM_to_12PM', 'Sunday_12PM_to_4PM', 
        			'Sunday_4PM_to_8PM', 'Sunday_after_8PM', 'help_description']
        
        labels = vendor_labels
        help_texts = vendor_help_texts

    def save(self, profile, commit=True):
      bid = super(VendorBidForm, self).save(commit=False)
      bid.bidder = profile
      bid.last_update =  datetime.datetime.utcnow().replace(tzinfo=utc)
      bid.type = "Panel"
      
      profile.user_object.first_name = self.cleaned_data['first_name']
      profile.user_object.last_name = self.cleaned_data['last_name']
      profile.user_object.email = self.cleaned_data['email']
      
      profile.onsite_phone = self.cleaned_data['onsite_phone']
      profile.address1 = self.cleaned_data['address1']
      profile.address2 = self.cleaned_data['address2']
      profile.city = self.cleaned_data['city']
      profile.state = self.cleaned_data['prof_state']
      profile.zip_code = self.cleaned_data['zip_code']
      profile.country = self.cleaned_data['country']
      profile.offsite_preferred = self.cleaned_data['offsite_preferred']
      
      if 'Submit' in self.data:
         bid.state = "Submitted"
      elif 'Draft' in self.data:
         bid.state = "Draft"
      if commit:
         bid.save()
         profile.save()
         profile.user_object.save()
         
    def clean(self):
		if 'Draft' in self.data:
			super(VendorBidForm, self).clean()
			if 'length_minutes' in self._errors:
				del self._errors['length_minutes']
			if 'description' in self._errors:
				del self._errors['description']
		else:
			super(VendorBidForm, self).clean()
		return self.cleaned_data


class AudioInfoForm(forms.ModelForm):
    class Meta:
        model=AudioInfo

class AudioInfoBidForm(forms.ModelForm):
    class Meta:
        model=AudioInfo
        fields=['title','artist']
        labels= audioinfo_labels
class LightingInfoForm(forms.ModelForm):
    class Meta:
        model=LightingInfo

class PropsInfoForm(forms.ModelForm):
    class Meta:
        model=PropsInfo


class LightingInfoBidForm(forms.ModelForm):
    class Meta:
        model=LightingInfo
        fields = []


class PropsInfoBidForm(forms.ModelForm):
    class Meta:
        model=PropsInfo
        fields=[]
    


    
