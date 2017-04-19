from django.forms import (
    ChoiceField,
    ModelForm,
)
from gbe.models import GenericEvent
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from gbetext import new_event_options


class GenericEventScheduleForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    type = ChoiceField(
        choices=new_event_options,
        help_text=event_help_texts['type'])

    class Meta:
        model = GenericEvent
        fields = [
            'e_title',
            'e_description',
            'duration',
            'type',
            'default_location', ]
        help_texts = event_help_texts
        labels = event_labels
