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
    eventitem_id = IntegerField(
        widget=HiddenInput,
        required=False)
    submitted = BooleanField(widget=HiddenInput, initial=True)
    e_title = CharField(
        widget=TextInput(attrs={'size': '79'}),
        label=classbid_labels['e_title'])
    e_description = CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        label=classbid_labels['e_description'])

    def save(self, commit=True):
        this_class = super(ClassBookingForm, self).save(commit=False)
        this_class.b_title = this_class.e_title
        if commit:
            this_class.save()
        return this_class

    class Meta:
        model = Class
        fields = ['type',
                  'e_title',
                  'e_description',
                  'maximum_enrollment',
                  'fee',
                  'accepted',
                  'submitted',
                  'eventitem_id',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
