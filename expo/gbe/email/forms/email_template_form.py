from django.forms import (
    CharField,
    HiddenInput,
    ModelForm,
    Textarea,
)
from post_office.models import EmailTemplate
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from tinymce.widgets import TinyMCE


class EmailTemplateForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    content = CharField(
        widget=Textarea(attrs={'cols': 80, 'rows': 15}))
    html_content = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    sender = CharField(max_length=100, required=True, label="From")

    class Meta:
        model = EmailTemplate
        fields = ['sender', 'name', 'subject', 'content', 'html_content']
        widgets = {'name': HiddenInput()}
        help_texts = event_help_texts
        labels = event_labels
