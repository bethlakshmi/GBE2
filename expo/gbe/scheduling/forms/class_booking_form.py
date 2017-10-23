from django.forms import (
    BooleanField,
    CharField,
    IntegerField,
    HiddenInput,
    ModelForm,
    TextInput,
)
from gbe.models import Class
from gbe_forms_text import (
    classbid_help_texts,
    classbid_labels,
)
from tinymce.widgets import TinyMCE


class ClassBookingForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    accepted = IntegerField(
        initial=3,
        widget=HiddenInput)
    submitted = BooleanField(widget=HiddenInput, initial=True)
    e_title = CharField(
        widget=TextInput(attrs={'size': '79'}),
        label=classbid_labels['e_title'])
    e_description = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        label=classbid_labels['e_description'])

    class Meta:
        model = Class
        fields = ['type',
                  'e_title',
                  'e_description',
                  'maximum_enrollment',
                  'fee',
                  'space_needs',
                  'accepted',
                  'submitted',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
