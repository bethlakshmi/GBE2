from gbe.models import Profile, Act
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [ 'display_name', 'phone', 
                   'address1', 'address2',
                  'city', 'state', 'zip_code', 'country',
                  ]



class RegistrationForm(UserCreationForm):
    '''Form for creating a GBE user. Collects info for User object as 
    well as for user's profile (Partificipant object)
    '''
    email = forms.EmailField(required=True)
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
        

class ActForm(forms.ModelForm):
    class Meta:
        model = Act


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
    
    
