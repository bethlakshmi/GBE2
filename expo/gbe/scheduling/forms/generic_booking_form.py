from django.forms import (
    CharField,
    HiddenInput,
    ModelForm,
)
from gbe.models import GenericEvent
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from tinymce.widgets import TinyMCE


class GenericBookingForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    e_description = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        label=event_labels['e_description'])

    class Meta:
        model = GenericEvent
        fields = [
            'e_title',
            'e_description',
            'type',
            'e_conference', ]
        help_texts = event_help_texts
        labels = event_labels
        widgets = {'type': HiddenInput(),
                   'e_conference': HiddenInput()}
