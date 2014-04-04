from gbe.models import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
import datetime
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist

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
    def __init__(self, *args, **kwargs):
      super(ActBidForm, self).__init__(*args, **kwargs)
      # this is dynamic for the festival experience, it's a supporting table
      # with a list of related festivals that may grow or change in time
      n = 8
      for festival in festival_list:
        try:
          initial_experience = PerformerFestivals.objects.get(actbid=kwargs['initial']['bidid'],festival=festival[0]).experience
        except ObjectDoesNotExist:
          initial_experience = "No"
        self.fields.insert(n,festival[0],forms.ChoiceField(choices=festival_experience, initial=initial_experience, label=festival[1]))
        n += 1

    required_css_class = 'required'
    error_css_class = 'error'
    
    # Needed info about bidder
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True, 
          help_text='A phone number we can use to reach you when you are at the Expo, such as cell phone.')

	# Forced required when in submission (not draft)
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
          help_text='A phone number we can use to reach you when you are at the Expo, such as cell phone.')

	# Forced required when in submission (not draft)
    title = forms.CharField(required=True, label='Class')
    length_minutes = forms.CharField(required=True, label='Class Length', error_messages={
                'required': ("Class Length (in minutes) is required."),
                'max_length': ("The Class Length  is too long.") },
          help_text='Length class in minutes - please note that classes are asked to end 10 minutes shorter than the full slot length, so a 60 minute class is really 50 minutes.') 
    description = forms.CharField(widget=forms.Textarea, required=True, error_messages={
                'required': ("Description of the Class is required."),
                'max_length': ("The Description  is too long.") },
          help_text='For use on the The Great Burlesque Expo website, in advertising and in any schedule of events. The description should be 1-2 paragraphs.')
	# removing panels as a choice, panels have their own form.
    type = forms.ChoiceField(choices=(('Lecture', "Lecture"), ('Movement', "Movement"),
                      ('Workshop',"Workshop")))
    class Meta:
        model = ClassBid
        fields = [ 'email', 'onsite_phone', 'title', 'organization', 'homepage', 
                   'length_minutes', 'type', 'description', 'min_size', 'max_size', 
                   'history', 'other_teachers', 'run_before', 'fee', 'space_needs',
                   'physical_restrictions', 'schedule_constraints','multiple_run']
        
        labels = {
            'min_size': ('Minimum Size'),
            'max_size': ('Maxiumum Size'),
            'history': ('Previous Experience'),
            'other_teachers': ('Fellow Teachers'),
            'run_before': 'Has the Class been run Before?',
            'fee': 'Materials Fee',
            'space_needs': 'Room Preferences',
            'physical_restrictions': 'Physical Restrictions',
            'schedule_constraints': 'Scheduling Constraints',
            'multiple_run': 'Are you willing to run the class more than once?',
        }
        help_texts = {
            'min_size': ('The minimum number of people required for your class. This guideline helps the convention meet both teacher expectations and class size needs. If you\'re not sure, make the minimum 1'),
            'max_size': ('The maximum number of people that the class can accomodate.'),
            'history': ('Previous Experience'),
            'other_teachers': ('This is a preliminary list. You\'ll be asked to confirm fellow teachers if the class is confirmed.  Additional teachers are eligible for discounts, however a large number of teachers for a single event is likely to diminish the discount level provided for the group. '),
            'run_before': ('Has the Class been run Before?'),
            'fee': ('Materials Fee'),
            'space_needs': ('Room Preferences'),
            'physical_restrictions': ('Physical Restrictions'),
            'schedule_constraints': ('Scheduling Constraints'),
            'multiple_run': ('Are you willing to run the class more than once?'),
        }

    def save(self, profile, commit=True):
      classbid = super(ClassBidForm, self).save(commit=False)
      classbid.bidder = profile
      classbid.last_update =  datetime.datetime.utcnow().replace(tzinfo=utc)
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
			return self.cleaned_data
		else:
			super(ClassBidForm, self).clean()
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
			return self.cleaned_data

class PanelBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    
    # Needed information about Bidder
    email = forms.EmailField(required=True)
    onsite_phone = forms.CharField(required=True, 
          help_text='A phone number we can use to reach you when you are at the Expo, such as cell phone.')

	# Forced required when in submission (not draft)
    title = forms.CharField(required=True, label='Panel')
    length_minutes = forms.CharField(initial=60, widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.Textarea, required=True, error_messages={
                'required': ("Description of the Class is required."),
                'max_length': ("The Description  is too long.") },
          help_text='For use on the The Great Burlesque Expo website, in advertising and in any schedule of events. The description should be 1-2 paragraphs.')
	# removing panels as a choice, panels have their own form.
    space_options = forms.CharField(initial="4", widget=forms.HiddenInput())
    type = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ClassBid
        fields = [ 'email', 'onsite_phone', 'title', 'length_minutes',  
        		   'description', 'other_teachers', 'run_before','space_options', 'type']
        
        labels = {
            'other_teachers': ('Recommended Panelists'),
            'run_before': 'Has the Panel been run Before?',
        }
        help_texts = {
            'other_teachers': ('It is far more likely that your panel may be run at The Great Burlesque Expo 2014if we can find qualified panelists and a moderator - let us know any recommendations.'),
            'run_before': ('The Great Burlesque Expo 2014 is looking for convention content that is new and that have successfully presented before, either at a convention, or elsewhere. If this content has run before, please describe where and when.'),
        }

    def save(self, profile, commit=True):
      bid = super(PanelBidForm, self).save(commit=False)
      bid.bidder = profile
      bid.last_update =  datetime.datetime.utcnow().replace(tzinfo=utc)
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
         


#class ShowForm(forms.ModelForm):
#    class Meta:
#        model = Show
#        fields = ['title', 'organizer', 'mc', 'acts', 
#
#                  'short_desc', 'long_desc']
    
    
