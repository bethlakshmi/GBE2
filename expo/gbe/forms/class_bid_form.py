from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ModelForm,
    MultipleChoiceField,
    Textarea,
)
from gbe.models import Class
from gbe_forms_text import (
    classbid_help_texts,
    classbid_labels,
    class_schedule_options
)


class ClassBidDraftForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    schedule_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        required=False,
        label=classbid_labels['schedule_constraints']
    )
    avoided_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['avoided_constraints'],
        required=False)
    b_description = CharField(
        required=True,
        widget=Textarea,
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


class ClassBidForm(ClassBidDraftForm):
    schedule_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['schedule_constraints'])
    b_description = CharField(
        required=True,
        widget=Textarea,
        label=classbid_labels['b_description'])

