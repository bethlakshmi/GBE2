from django.forms import (
    CharField,
    EmailField,
    ModelForm,
    Textarea,
    TextInput,
)
from post_office.models import Email
from gbe_forms_text import (
    event_labels,
)
from tinymce.widgets import TinyMCE
from django.utils.html import strip_tags


class AdHocEmailForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    html_message = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}),
        label="Message")
    sender = EmailField(required=True,
                        label="From")
    subject = CharField(widget=TextInput(attrs={'size': '79'}))

    class Meta:
        model = Email
        fields = ['sender', 'subject', 'html_message']
        labels = event_labels
