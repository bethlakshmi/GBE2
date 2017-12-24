from django.forms import (
    CharField,
    HiddenInput,
    ModelForm,
)
from gbe.models import Show
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from tinymce.widgets import TinyMCE


class ShowBookingForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    e_description = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        label=event_labels['e_description'])

    class Meta:
        model = Show
        fields = [
            'e_title',
            'e_description',
            'e_conference', ]
        help_texts = event_help_texts
        labels = event_labels
        widgets = {'e_conference': HiddenInput()}
