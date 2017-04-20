from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    HiddenInput,
    ModelForm,
    MultipleChoiceField,
    Textarea,
)
from gbe.models import Vendor
from gbe_forms_text import (
    vendor_help_texts,
    vendor_labels,
    vendor_schedule_options,
)
from gbe.expoformfields import FriendlyURLInput


class VendorBidForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    b_description = CharField(
        required=True,
        widget=Textarea,
        help_text=vendor_help_texts['description'],
        label=vendor_labels['description'])
    help_times = MultipleChoiceField(widget=CheckboxSelectMultiple,
                                           choices=vendor_schedule_options,
                                           required=False,
                                           label=vendor_labels['help_times'])

    class Meta:
        model = Vendor
        fields = ['b_title',
                  'b_description',
                  'profile',
                  'website',
                  'physical_address',
                  'publish_physical_address',
                  'logo',
                  'want_help',
                  'help_description',
                  'help_times',
                  ]
        help_texts = vendor_help_texts
        labels = vendor_labels
        widgets = {'accepted': HiddenInput(),
                   'submitted': HiddenInput(),
                   'profile': HiddenInput(),
                   'website': FriendlyURLInput,
                   }
