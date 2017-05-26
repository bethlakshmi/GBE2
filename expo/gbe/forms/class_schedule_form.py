from django.forms import (
    BooleanField,
    ChoiceField,
    HiddenInput,
    ModelChoiceField,
    ModelForm,
)
from gbe.models import Class
from gbe_forms_text import (
    acceptance_note,
    classbid_help_texts,
    classbid_labels,
)
from gbetext import acceptance_states
from gbe.forms.common_queries import visible_personas


class ClassScheduleForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    accepted = ChoiceField(
        choices=acceptance_states,
        initial=3,
        help_text=acceptance_note)
    teacher = ModelChoiceField(queryset=visible_personas)
    submitted = BooleanField(widget=HiddenInput, initial=True)

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
                  'submitted',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
