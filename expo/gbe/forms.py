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
        fields = [ 'stage_name', 'display_name',
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
        fields = [ 'email', 'first_name', 'last_name', 'stage_name',
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
      if self.cleaned_data['stage_name'] is None or self.cleaned_data['stage_name'] == '':
        partform.display_name = self.cleaned_data['first_name']+" "+self.cleaned_data['last_name']
      else:
        partform.display_name = self.cleaned_data['stage_name']
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

class RegistrationForm(UserCreationForm):
    '''Form for creating a GBE user. Collects info for User object as
		well as for user's profile (Partificipant object)
	'''
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model=User
        fields = {'username', 'first_name','last_name',
                  'email', 'password1', 'password2'}

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
        return user
        
class BidderInfoForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True,
          help_text=bidder_info_phone_error)

    class Meta:
        model = Profile
        fields = [ 'onsite_phone', 'email']
        

class ActBidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
      super(ActBidForm, self).__init__(*args, **kwargs)
      # this is dynamic for the festival experience, it's a supporting table
      # with a list of related festivals that may grow or change in time
      for (n, festival) in enumerate(festival_list, 8):
        try:
          initial_experience = PerformerFestivals.objects.get(
          			actbid=kwargs['initial']['bidid'],festival=festival[0]).experience
        except ObjectDoesNotExist:
          initial_experience = "No"
        self.fields.insert(n,festival[0],forms.ChoiceField(choices=festival_experience, 
        			initial=initial_experience, label=festival[1]))


    required_css_class = 'required'
    error_css_class = 'error'
    
    # Needed info about bidder
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True,
          help_text=bidder_info_phone_error)

# Forced required when in submission (not draft)
    title = forms.CharField(required=True, label='Title of Act')
    bio = forms.CharField(widget=forms.Textarea, required=True, label='History',
          error_messages={'required': bio_required, 'max_length': bio_too_long },
          help_text=bio_help_text)
    description = forms.CharField(widget=forms.Textarea, required=True, error_messages={
                'required': act_description_required, 'max_length': act_description_too_long },
          		help_text=act_description_help_text)
    act_length = forms.TimeField(input_formats=['%M:%S'],
                                 required=True,
                                 error_messages={'blank':act_length_required,
                                                 'null':act_length_required,
                                                 'invalid':act_length_help_text})
    promo_image = forms.FileField(required=True, label='Publicity Picture',
          error_messages={ 'required': promo_required }, help_text=promo_help_text)

    class Meta:
        model = ActBid
        fields = [ 'email', 'onsite_phone', 'name', 'title', 'homepage', 'is_group',
                   'other_performers', 'experience', 'bio', 'song_name', 'artist',
                   'act_length', 'description', 'video_choice', 'video_link',
                   'promo_image', 'hotel_choice', 'volunteer_choice', 'conference_choice' ]
        
        required = { 'title', 'bio', 'act_length', 'description', 'promo_image' }
        labels = actbid_labels
        help_texts = actbid_help_texts
        error_messages = actbid_error_messages
    def save(self, profile, commit=True):
        actbid = super(ActBidForm, self).save(commit=False)
        actbid.bidder = profile
        actbid.last_update = datetime.datetime.utcnow().replace(tzinfo=utc)
        profile.onsite_phone = self.cleaned_data['onsite_phone']
        profile.user_object.email = self.cleaned_data['email']
        if self.cleaned_data['is_group'] == "No" and self.cleaned_data['name'] != '':
            profile.stage_name = self.cleaned_data['name']
            profile.display_name = self.cleaned_data['name']
        for festival in festival_list:
            try:
                festival_experience = PerformerFestivals.objects.get(actbid=6,festival=festival[0])
                festival_experience.experience = experience=self.cleaned_data.get(festival[0])
            except ObjectDoesNotExist:
                festival_experience = PerformerFestivals(
                    experience=self.cleaned_data.get(festival[0]),
                    festival=festival[0],
                    actbid=actbid)
                if commit:
                    festival_experience.save()
        if 'Submit' in self.data:
            actbid.state = "Submitted"
        elif 'Draft' in self.data:
            actbid.state = "Draft"
        if commit:
            actbid.save()
            profile.save()
            profile.user_object.save()
         
    def clean(self):
      if 'Draft' in self.data:
        super(ActBidForm, self).clean()
        for field in ['bio', 'act_length', 'description', 'promo_image']:
            if field in self._errors:
                del self._errors[field]

      else:
        super(ActBidForm, self).clean()
        is_group = self.cleaned_data.get('is_group')
        name = self.cleaned_data.get('name')
        others = self.cleaned_data.get('other_performers')
        group_err = False
        if is_group == "Yes" and others == '':
            group_err = True
            self._errors['other_performers']=self.error_class(actbid_otherperformers_missing)
            self._errors['is_group']=self.error_class(actbid_group_wrong)
        if name == '':
            group_err = True
            self._errors['name']=self.error_class(actbid_name_missing)
        if group_err:
            raise forms.ValidationError(actbid_group_error)
        video_choice = self.cleaned_data.get('video_choice')
        video_link = self.cleaned_data.get('video_link')
        if video_choice != "0" and video_link == '':
            self._errors['video_choice']=self.error_class(video_error1)
            self._errors['video_link']=self.error_class(video_error2)
            raise forms.ValidationError(video_error3)
        for festival in festival_list:
            match = False
            for answer in festival_experience:
                match = self.cleaned_data.get(festival[0]) == answer[0]

      return self.cleaned_data


class ClassBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    
    # Needed information about Bidder
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True,
          help_text=bidder_info_phone_error)

# Forced required when in submission (not draft)
    title = forms.CharField(required=True, label='Class')
    description = forms.CharField(widget=forms.Textarea, required=True, error_messages={
                'required': description_required, 'max_length': description_too_long },
          		help_text=description_help_text)
# removing panels as a choice, panels have their own form.
    type = forms.ChoiceField(choices=(('Lecture', "Lecture"), ('Movement', "Movement"),
                      ('Workshop',"Workshop")))
    class Meta:
        model = ClassBid
        fields = [ 'email', 'onsite_phone', 'title', 'organization', 'homepage',
                   'length_minutes', 'type', 'description', 'min_size', 'max_size',
                   'history', 'other_teachers', 'run_before', 'fee', 'space_needs',
                   'physical_restrictions', 'schedule_constraints','multiple_run']
        
        labels = classbid_labels
        help_texts = classbid_help_texts

    def save(self, profile, commit=True):
      classbid = super(ClassBidForm, self).save(commit=False)
      classbid.bidder = profile
      classbid.last_update = datetime.datetime.utcnow().replace(tzinfo=utc)
      profile.onsite_phone = self.cleaned_data['onsite_phone']
      profile.user_object.email = self.cleaned_data['email']
      if 'Submit' in self.data:
         classbid.state = "Submitted"
      elif 'Draft' in self.data:
         classbid.state = "Draft"
      if commit:
         classbid.save()
         profile.save()
         profile.user_object.save()
         
    def clean(self):
      if 'Draft' in self.data:
        super(ClassBidForm, self).clean()
        if 'length_minutes' in self._errors:
          del self._errors['length_minutes']
        if 'description' in self._errors:
          del self._errors['description']
      else:
        super(ClassBidForm, self).clean()
        type = self.cleaned_data.get('type')
        space_needs = self.cleaned_data.get('space_needs')
        if type == 'Workshop' and space_needs:
        	self._errors['type'] = space_error1
        	self._errors['space_needs'] = space_error1
        	raise forms.ValidationError(space_type_error1)
        elif type == 'Movement' and (space_needs == "3" or space_needs == "4" or 
        								space_needs == "5"):
        	self._errors['type'] = space_error2
        	self._errors['space_needs'] = space_error2
        	raise forms.ValidationError(space_type_error2)
        elif type == 'Lecture' and (space_needs == "0" or space_needs == "1" or 
        								space_needs == "2"):
        	self._errors['type'] = space_error3
        	self._errors['space_needs'] = space_error3
        	raise forms.ValidationError(space_type_error3)


      return self.cleaned_data

class PanelBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    
    # Needed information about Bidder
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True,
          help_text=bidder_info_phone_error)

# Forced required when in submission (not draft)
    title = forms.CharField(required=True, label='Panel')
    length_minutes = forms.CharField(initial=60, widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.Textarea, required=True, error_messages={
                'required': description_required, 'max_length': description_too_long },
          		help_text=description_help_text)
# removing panels as a choice, panels have their own form.
    space_options = forms.CharField(initial="4", widget=forms.HiddenInput())
    type = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ClassBid
        fields = [ 'email', 'onsite_phone', 'title', 'length_minutes',
         'description', 'other_teachers', 'run_before','space_options', 'type']
        
        labels = panel_labels
        help_texts = panel_help_texts

    def save(self, profile, commit=True):
      bid = super(PanelBidForm, self).save(commit=False)
      bid.bidder = profile
      bid.last_update = datetime.datetime.utcnow().replace(tzinfo=utc)
      bid.type = "Panel"
      profile.onsite_phone = self.cleaned_data['onsite_phone']
      profile.user_object.email = self.cleaned_data['email']
      if 'Submit' in self.data:
         bid.state = "Submitted"
      elif 'Draft' in self.data:
         bid.state = "Draft"
      if commit:
         bid.save()
         profile.save()
         profile.user_object.save()
         


         
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
