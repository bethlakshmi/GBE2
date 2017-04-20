from gbe.models import (
    Act,
    Class,
)
from django import forms
from gbe_forms_text import *
from gbetext import (
    act_other_perf_options,
    act_shows_options,
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
