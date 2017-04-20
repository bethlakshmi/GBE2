from gbe.models import (
    Act,
    AudioInfo,
    Class,
    Costume,
)
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from gbe_forms_text import *
from gbetext import (
    act_other_perf_options,
    act_shows_options,
    boolean_options,
)
from gbe.expoformfields import (
    DurationFormField,
)


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
