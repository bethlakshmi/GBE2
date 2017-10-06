from django.forms import (
    CharField,
    ChoiceField,
    Form,
    HiddenInput,
    ModelChoiceField,
)
from gbetext import acceptance_states
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from gbe.models import Conference


class SelectBidderForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    conference = ModelChoiceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        empty_label=("All"),
        required=False)
    bid_type = ChoiceField(required=False)
    state = ChoiceField(choices=((('', 'All'),) + acceptance_states),
                        required=False)


class SecretBidderInfoForm(SelectBidderForm):
    conference = ModelChoiceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        widget=HiddenInput())
    bid_type = ChoiceField(widget=HiddenInput())
    state = ChoiceField(widget=HiddenInput())
