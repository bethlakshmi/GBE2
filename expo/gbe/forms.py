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
    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = [ 'stage_name', 'display_name', 'address1', 'address2', 'city', 
                   'state', 'zip_code', 'country', 'onsite_phone', 
                   'best_time', 'how_heard', 'preferred_contact'
                  ]
        # overload save to make sure there is always a display name


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

    class Meta:
        model = ActBid
        fields = [ 'email', 'onsite_phone', 'name', 'title', 'homepage', 'is_group',  
                   'other_performers', 'experience', 'bio', 'song_name', 'artist', 
                   'act_length', 'description', 'video_choice', 'video_link', 
                   'promo_image', 'hotel_choice', 'volunteer_choice', 'conference_choice' ]
        
        labels = {
            'title': ('Title of Act'),
            'name': ('Stage Name or Troupe'),
            'homepage': ('Web Site'),
            'is_group': ('Is this a Troupe Performance?'),
            'other_performers': ('Fellow performers'),
            'bio': ('History'),
            'song_name': 'Title of Song',
            'artist': 'Name of Artist',
            'act_length': 'Act Length',
            'video_choice': 'Video Description',
            'video_link': 'Link to Video',
            'promo_image': 'Publicity Picture',
            'hotel_choice': 'Are you staying in the hotel?',
            'volunteer_choice': 'Are you volunteering for the event?',
            'conference_choice': 'Are you attending the conference?',

        }
        help_texts = {
            'name': ('If you are a soloist, this is your stage name.  If you are a troupe, this is your troupe name.  If you are a group, but not a troupe, please give the names you would like to be introduced by.'),
            'other_performers': ('Please list other people involved/required for this act.'),
            'bio': ('Please give a brief performer/troupe history.'),
            'act_length': ('Length of entire act in mm:ss - please include any time you are performing before or after your song.'),
            'description': ('Please give a brief description of your act. Stage kittens will retrieve costumes and props, but we cannot clean the stage after your act. Please do not leave anything on the stage (water, glitter, confetti, etc.)'),
            'promo_image': ('Please_upload a photograph of yourself (photo must be under 10 MB)')
        }
        error_messages = {
            'title': {
                'required': ("The Title is required."),
                'max_length': ("The title of the act is too long."),
            },

            
            'bio': {
                'required': ("Performer/Troupe history is required."),
                'max_length': ("The History  is too long."),
            },

            'act_length': {
                'required': ("Act Length (mm:ss) is required."),
                'max_length': ("The Act Length  is too long."),
            },

            'description': {
                'required': ("Description of the Act is required."),
                'max_length': ("The Description  is too long."),
            },

            'promo_image': {
                'required': ("Please provide a photo."),
            },

        }
    def save(self, profile, commit=True):
      actbid = super(ActBidForm, self).save(commit=False)
      actbid.bidder = profile
      actbid.last_update =  datetime.datetime.now()
      profile.onsite_phone = self.cleaned_data['onsite_phone']
      profile.user_object.email = self.cleaned_data['email']
      if 'Submit' in self.data:
         actbid.state = "Submitted"
      elif 'Draft' in self.data:
         actbid.state = "Draft"
      if commit:
         actbid.save()
         profile.save()
         profile.user_object.save()

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
    
    
