from django.forms import (
    CharField,
    EmailField,
    Form,
    Textarea,
    TextInput,
)
from tinymce.widgets import TinyMCE
from django.utils.html import strip_tags


class AdHocEmailForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    sender = EmailField(required=True,
                        label="From")
    subject = CharField(widget=TextInput(attrs={'size': '79'}))
    html_message = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}),
        label="Message")
