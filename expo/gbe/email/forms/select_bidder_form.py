from django.forms import (
    CharField,
    Form,
    HiddenInput,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from gbetext import acceptance_states
from gbe_forms_text import (
    event_help_texts,
    event_labels,
)
from gbe.models import Conference


class SelectBidderForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    conference = ModelMultipleChoiceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        widget=CheckboxSelectMultiple(attrs={"checked":""}),
        required=False,)
    bid_type = MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={"checked":""}))
    state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=CheckboxSelectMultiple(),
        required=True)


class SecretBidderInfoForm(SelectBidderForm):
    conference = ModelMultipleChoiceField(
        queryset=Conference.objects.all().order_by('conference_name'),
        widget=MultipleHiddenInput(),
        required=False)
    bid_type = MultipleChoiceField(widget=HiddenInput(),
                           required=False)
    state = MultipleChoiceField(
        choices=((('Draft', 'Draft'),) + acceptance_states),
        widget=MultipleHiddenInput(),
        required=True)
