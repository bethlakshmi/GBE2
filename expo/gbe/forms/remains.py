from gbe.models import (
    Act,
    AudioInfo,
    AvailableInterest,
    Class,
    Costume,
    StageInfo,
    Vendor,
)
from django import forms
from django.forms import ModelMultipleChoiceField
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.timezone import utc
from django.core.exceptions import ObjectDoesNotExist
from gbe_forms_text import *
from gbetext import (
    act_other_perf_options,
    act_shows_options,
    boolean_options,
)
from gbe.expoformfields import (
    DurationFormField,
    FriendlyURLInput,
)
from gbe.functions import get_current_conference
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


class UserCreateForm(UserCreationForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = forms.EmailField(required=True)
    username = forms.CharField(label=username_label, help_text=username_help)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    def is_valid(self):
        valid = super(UserCreateForm, self).is_valid()

        if valid:
            email = self.cleaned_data['email']
            if User.objects.filter(email=email).count():
                self._errors['email'] = 'That email address is already in use'
                valid = False
        return valid

    class Meta:
        model = User
        fields = ['username',
                  'email',
                  'first_name',
                  'last_name',
                  'password1',
                  'password2',
                  ]


class ActEditForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(
        required=True,
        help_text=act_help_texts['act_duration']
    )
    track_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['track_duration'],
        label=act_bid_labels['track_duration']
    )
    track_artist = forms.CharField(required=False)
    track_title = forms.CharField(required=False)
    shows_preferences = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=act_shows_options,
        label=act_bid_labels['shows_preferences'],
        help_text=act_help_texts['shows_preferences']
    )
    other_performance = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=act_other_perf_options,
        label=act_bid_labels['other_performance'],
        help_text=act_help_texts['other_performance'],
        required=False,
    )
    b_description = forms.CharField(
        required=True,
        label=act_bid_labels['description'],
        help_text=act_help_texts['description'],
        widget=forms.Textarea)

    class Meta:
        model = Act
        fields, required = Act().bid_fields
        fields += ['act_duration',
                   'track_duration',
                   'track_artist',
                   'track_title']
        labels = act_bid_labels
        help_texts = act_help_texts
        widgets = {'b_conference': forms.HiddenInput(), }


class ActEditDraftForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['act_duration']
    )
    track_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['track_duration'],
        label=act_bid_labels['track_duration']
    )
    track_artist = forms.CharField(required=False)
    track_title = forms.CharField(required=False)
    shows_preferences = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=act_shows_options,
        label=act_bid_labels['shows_preferences'],
        help_text=act_help_texts['shows_preferences'],
        required=False
    )
    other_performance = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=act_other_perf_options,
        label=act_bid_labels['other_performance'],
        help_text=act_help_texts['other_performance'],
        required=False
    )
    b_conference = forms.HiddenInput()

    class Meta:
        model = Act
        fields, required = Act().bid_fields
        fields += ['act_duration',
                   'track_duration',
                   'track_artist',
                   'track_title']
        required = Act().bid_draft_fields
        labels = act_bid_labels
        help_texts = act_help_texts
        widgets = {'b_conference': forms.HiddenInput(), }


class ClassBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    schedule_constraints = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['schedule_constraints'])
    avoided_constraints = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['avoided_constraints'],
        required=False)
    b_description = forms.CharField(
        required=True,
        widget=forms.Textarea,
        label=classbid_labels['b_description'])

    class Meta:
        model = Class
        fields = ['b_title',
                  'teacher',
                  'b_description',
                  'maximum_enrollment',
                  'type',
                  'fee',
                  'length_minutes',
                  'history',
                  'schedule_constraints',
                  'avoided_constraints',
                  'space_needs']
        help_texts = classbid_help_texts
        labels = classbid_labels


class ClassBidDraftForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    schedule_constraints = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=class_schedule_options,
        required=False,
        label=classbid_labels['schedule_constraints']
    )
    avoided_constraints = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['avoided_constraints'],
        required=False)

    class Meta:
        model = Class
        fields, requiredsubmit = Class().get_bid_fields
        required = Class().get_draft_fields
        help_texts = classbid_help_texts
        labels = classbid_labels


class RehearsalSelectionForm(forms.Form):
    show = forms.CharField(widget=forms.TextInput(
        attrs={'readonly': 'readonly'})
    )
    show_private = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(RehearsalSelectionForm, self).__init__(*args, **kwargs)
        if 'rehearsal' in kwargs['initial']:
            self.fields['rehearsal'] = forms.ChoiceField(
                choices=kwargs['initial']['rehearsal_choices'],
                initial=kwargs['initial']['rehearsal'])
        else:
            self.fields['rehearsal'] = forms.ChoiceField(
                choices=kwargs['initial']['rehearsal_choices'])

    class Meta:
        fields = ['show_private', 'show', 'rehearsal']


class VendorBidForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    b_description = forms.CharField(
        required=True,
        widget=forms.Textarea,
        help_text=vendor_help_texts['description'],
        label=vendor_labels['description'])
    help_times = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                           choices=vendor_schedule_options,
                                           required=False,
                                           label=vendor_labels['help_times'])

    class Meta:
        model = Vendor
        fields = ['b_title',
                  'b_description',
                  'profile',
                  'website',
                  'physical_address',
                  'publish_physical_address',
                  'logo',
                  'want_help',
                  'help_description',
                  'help_times',
                  ]
        help_texts = vendor_help_texts
        labels = vendor_labels
        widgets = {'accepted': forms.HiddenInput(),
                   'submitted': forms.HiddenInput(),
                   'profile': forms.HiddenInput(),
                   'website': FriendlyURLInput,
                   }


class ActTechInfoForm(forms.ModelForm):
    form_title = "Act Tech Info"
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Act
        fields = ['b_title',
                  'b_description',
                  'performer',
                  'video_link',
                  'video_choice']
        widgets = {'video_link': FriendlyURLInput}
        labels = act_bid_labels


class AudioInfoForm(forms.ModelForm):
    form_title = "Audio Info"
    required_css_class = 'required'
    error_css_class = 'error'
    track_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['track_duration'],
        label=act_bid_labels['track_duration']
    )

    class Meta:
        model = AudioInfo
        fields = '__all__'


class AudioInfoSubmitForm(forms.ModelForm):
    form_title = "Audio Info"
    required_css_class = 'required'
    error_css_class = 'error'
    track_duration = DurationFormField(
        required=False,
        help_text=act_help_texts['track_duration'],
        label=act_bid_labels['track_duration']
    )

    class Meta:
        model = AudioInfo
        fields = '__all__'

    def clean(self):
        # run the parent validation first
        cleaned_data = super(AudioInfoSubmitForm, self).clean()

        # doing is_complete doesn't work, that executes the pre-existing
        # instance, not the current data
        if not (
                (self.cleaned_data['track_title'] and
                 self.cleaned_data['track_artist'] and
                 self.cleaned_data['track_duration']
                 ) or
                self.cleaned_data['confirm_no_music']):
            raise ValidationError(
                ('Incomplete Audio Info - please either provide Track Title,'
                 'Artist and Duration, or confirm that there is no music.'),
                code='invalid')
        return cleaned_data


class StageInfoForm(forms.ModelForm):
    form_title = "Stage Info"
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(required=False,
                                     help_text=act_help_texts['act_duration'])

    class Meta:
        model = StageInfo
        labels = prop_labels
        help_texts = act_help_texts
        fields = '__all__'


class StageInfoSubmitForm(forms.ModelForm):
    form_title = "Stage Info"
    required_css_class = 'required'
    error_css_class = 'error'
    act_duration = DurationFormField(required=False,
                                     help_text=act_help_texts['act_duration'])

    class Meta:
        model = StageInfo
        labels = prop_labels
        help_texts = act_help_texts
        fields = '__all__'

    def clean(self):
        # run the parent validation first
        cleaned_data = super(StageInfoSubmitForm, self).clean()
        # doing is_complete doesn't work, that executes the pre-existing
        # instance, not the current data

        if not (self.cleaned_data['set_props'] or
                self.cleaned_data['clear_props'] or
                self.cleaned_data['cue_props'] or
                self.cleaned_data['confirm']):
            raise ValidationError(
                '''Incomplete Prop Info - please either check of whether props
                must set, cleaned up or provided on cue, or confirm that no
                props or set pieces are needed.''',
                code='invalid')

        return cleaned_data


class CostumeBidDraftForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    active_use = forms.TypedChoiceField(
        widget=forms.RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['active_use'],
        required=False)
    debut_date = forms.CharField(
        label=costume_proposal_labels['debut_date'],
        help_text=costume_proposal_help_texts['debut_date'],
        widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'}),
        required=False)

    class Meta:

        model = Costume
        fields = ['b_title',
                  'performer',
                  'creator',
                  'act_title',
                  'debut_date',
                  'active_use']
        help_texts = costume_proposal_help_texts
        labels = costume_proposal_labels


class CostumeBidSubmitForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    active_use = forms.TypedChoiceField(
        widget=forms.RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['active_use'])
    debut_date = forms.CharField(
        label=costume_proposal_labels['debut_date'],
        help_text=costume_proposal_help_texts['debut_date'],
        widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'}),
        required=False)

    class Meta:

        model = Costume
        fields = ['b_title',
                  'performer',
                  'creator',
                  'act_title',
                  'debut_date',
                  'active_use']
        help_texts = costume_proposal_help_texts
        labels = costume_proposal_labels


class CostumeDetailsDraftForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    form_title = "Costume Information"

    pasties = forms.TypedChoiceField(
        widget=forms.RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['pasties'],
        required=False)
    pieces = forms.ChoiceField(choices=[(x, x) for x in range(1, 21)],
                               label=costume_proposal_labels['pieces'],
                               required=False)
    dress_size = forms.ChoiceField(
        choices=[(x, x) for x in range(1, 21)],
        label=costume_proposal_labels['dress_size'],
        help_text=costume_proposal_help_texts['dress_size'],
        required=False)
    b_description = forms.CharField(
        max_length=500,
        widget=forms.Textarea,
        label=costume_proposal_labels['description'],
        required=False)
    more_info = forms.CharField(
        max_length=500,
        widget=forms.Textarea,
        label=costume_proposal_labels['more_info'],
        required=False)

    class Meta:

        model = Costume
        fields = ['pieces',
                  'b_description',
                  'pasties',
                  'dress_size',
                  'more_info',
                  'picture']
        help_texts = costume_proposal_help_texts
        labels = costume_proposal_labels


class CostumeDetailsSubmitForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    form_title = "Costume Information"

    pasties = forms.TypedChoiceField(
        widget=forms.RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['pasties'])
    pieces = forms.ChoiceField(
        choices=[(x, x) for x in range(1, 21)],
        label=costume_proposal_labels['pieces'])
    dress_size = forms.ChoiceField(
        choices=[(x, x) for x in range(1, 21)],
        label=costume_proposal_labels['dress_size'],
        help_text=costume_proposal_help_texts['dress_size'])
    b_description = forms.CharField(
        max_length=500,
        widget=forms.Textarea,
        label=costume_proposal_labels['description'])
    more_info = forms.CharField(max_length=500,
                                widget=forms.Textarea,
                                label=costume_proposal_labels['more_info'],
                                required=False)
    picture = forms.FileField(label=costume_proposal_labels['picture'],
                              help_text=costume_proposal_help_texts['picture'])

    class Meta:

        model = Costume
        fields = ['pieces',
                  'b_description',
                  'pasties',
                  'dress_size',
                  'more_info',
                  'picture']
        help_texts = costume_proposal_help_texts
        labels = costume_proposal_labels
