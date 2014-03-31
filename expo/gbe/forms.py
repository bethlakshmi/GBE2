from gbe.models import Profile, Act, Bio, TechInfo, ActBid
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
import datetime
from django.utils.timezone import utc

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
        labels = {
            'address1': ('Street Address'),
            'address2': ('Street Address (cont.)'),
        }
        help_texts = {
            'stage_name': ('The name used in your performance.  The Expo will include this name in advertising, and it will be on your badge.  If you leave it blank, we will use first and last name.'),
            'onsite_phone': ('A phone number we can use to reach you when you are at the Expo, such as cell phone.'),
            'offsite_preferred': ('Your preferred phone number (if different from above), for communication before the Expo.  Use this if you prefer to get phone calls at a phone you cannot bring to the Expo.'),
        }

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
				self._errors['onsite_phone']=self.error_class(['Phone number needed here'])
				self._errors['offsite_preferred']=self.error_class(['... or here...'])
				self._errors['preferred_contact']=self.error_class(['...or choose a contact method that does not require a phone.'])
				raise forms.ValidationError('If Preferred contact is a Phone call or Text, we need your phone number as either an Onsite phone or Offsite preferred.')
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
        return  user
        
class BidderInfoForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True, 
          help_text='A phone number we can use to reach you when you are at the Expo, such as cell phone.')

    class Meta:
        model = Profile
        fields = [ 'onsite_phone', 'email']
        

class ActBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True, 
          help_text='A phone number we can use to reach you when you are at the Expo, such as cell phone.')
    title = forms.CharField(required=True, label='Title of Act')
    act_length = forms.CharField(required=True, label='Act Length', error_messages={
                'required': ("Act Length (mm:ss) is required."),
                'max_length': ("The Act Length  is too long.") },
          help_text='Length of entire act in mm:ss - please include any time you are performing before or after your song.') 
    bio = forms.CharField(widget=forms.Textarea, required=True, label='History', 
          error_messages={
                'required': ("Performer/Troupe history is required."),
                'max_length': ("The History  is too long.") },
          help_text='Please give a brief performer/troupe history.')
    description = forms.CharField(widget=forms.Textarea, required=True, error_messages={
                'required': ("Description of the Act is required."),
                'max_length': ("The Description  is too long.") },
          help_text='Please give a brief description of your act. Stage kittens will retrieve costumes and props, but we cannot clean the stage after your act. Please do not leave anything on the stage (water, glitter, confetti, etc.)')
    promo_image = forms.FileField(required=True, label='Publicity Picture', 
          error_messages={ 'required': ("Please provide a photo.") },
          help_text='Please_upload a photograph of yourself (photo must be under 10 MB).')

    class Meta:
        model = ActBid
        fields = [ 'email', 'onsite_phone', 'name', 'title', 'homepage', 'is_group',  
                   'other_performers', 'experience', 'bio', 'song_name', 'artist', 
                   'act_length', 'description', 'video_choice', 'video_link', 
                   'promo_image', 'hotel_choice', 'volunteer_choice', 'conference_choice' ]
        
        required = { 'title', 'bio', 'act_length', 'description', 'promo_image' }
        labels = {
            'name': ('Stage Name or Troupe'),
            'homepage': ('Web Site'),
            'is_group': ('Is this a Troupe Performance?'),
            'other_performers': ('Fellow performers'),
            'song_name': 'Title of Song',
            'artist': 'Name of Artist',
            'video_choice': 'Video Description',
            'video_link': 'Link to Video',
            'hotel_choice': 'Are you staying in the hotel?',
            'volunteer_choice': 'Are you volunteering for the event?',
            'conference_choice': 'Are you attending the conference?',
        }
        help_texts = {
            'name': ('If you are a soloist, this is your stage name.  If you are a troupe, this is your troupe name.  If you are a group, but not a troupe, please give the names you would like to be introduced by.'),
            'other_performers': ('Please list other people involved/required for this act.'),
        }
        error_messages = {
            'title': {
                'required': ("The Title is required."),
                'max_length': ("The title of the act is too long."),
            },

        }
    def save(self, profile, commit=True):
      actbid = super(ActBidForm, self).save(commit=False)
      actbid.bidder = profile
      actbid.last_update =  datetime.datetime.utcnow().replace(tzinfo=utc)
      profile.onsite_phone = self.cleaned_data['onsite_phone']
      profile.user_object.email = self.cleaned_data['email']
      if self.cleaned_data['is_group'] == "No" and self.cleaned_data['name'] != '':
         profile.stage_name = self.cleaned_data['name']
         profile.display_name = self.cleaned_data['name']
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
			if 'title' in self._errors:
				del self._errors['title']
			if 'bio' in self._errors:
				del self._errors['bio']
			if 'act_length' in self._errors:
				del self._errors['act_length']
			if 'description' in self._errors:
				del self._errors['description']
			if 'promo_image' in self._errors:
				del self._errors['promo_image']
			return self.cleaned_data
		else:
			super(ActBidForm, self).clean()
			is_group = self.cleaned_data.get('is_group')
			name = self.cleaned_data.get('video_link')
			others = self.cleaned_data.get('other_performers')
			if is_group == "Yes":
				group_err = False
				if name == '':
					group_err = True
					self._errors['name']=self.error_class(['...a name is needed'])
				if others == '':
					group_err = True
					self._errors['other_performers']=self.error_class(['...please describe the other performers.'])
				if group_err:
					self._errors['is_group']=self.error_class(['If this is a group... other entries are needed.'])
					raise forms.ValidationError('The submission says this is a group act, but there are no other performers listed')
			video_choice = self.cleaned_data.get('video_choice')
			video_link = self.cleaned_data.get('video_link')
			if video_choice != "0" and video_link == '':
				self._errors['video_choice']=self.error_class(['Either say that no video is provided.'])
				self._errors['video_link']=self.error_class(['... or provide video'])
				raise forms.ValidationError('The Video Description suggests a Video Link would be provided, but none was provided.')
			return self.cleaned_data


#class ClassForm(forms.ModelForm):
#    class Meta:
#        model = Class
#        fields = ['title', 'organizer', 'teacher', 
#                  'short_desc', 'long_desc']

#class ShowForm(forms.ModelForm):
#    class Meta:
#        model = Show
#        fields = ['title', 'organizer', 'mc', 'acts', 
#
#                  'short_desc', 'long_desc']
    
    
