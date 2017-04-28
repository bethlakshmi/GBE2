from django.forms import (
    ChoiceField,
    IntegerField,
    HiddenInput,
    ModelForm,
)
from gbe.models import Class
from gbe_forms_text import (
    acceptance_note,
    classbid_help_texts,
    classbid_labels,
)
from gbetext import acceptance_states


class ClassScheduleForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    accepted = IntegerField(
        initial=3,
        widget=HiddenInput)

    class Meta:
        model = Class
        fields = ['e_title',
                  'e_description',
                  'maximum_enrollment',
                  'type',
                  'fee',
                  'duration',
                  'space_needs',
                  'teacher',
                  'accepted',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
