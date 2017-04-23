from django.forms import ModelForm
from gbe.models import Show
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)


class ShowScheduleForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Show
        fields = ['e_title', 'e_description', 'duration', ]
        help_texts = event_help_texts
        labels = event_labels
