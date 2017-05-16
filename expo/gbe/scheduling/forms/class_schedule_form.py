from django.forms import (
    ChoiceField,
    IntegerField,
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
    accepted = IntegerField(
        initial=3,
        widget=HiddenInput)
    teacher = ModelChoiceField(queryset=visible_personas)

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
