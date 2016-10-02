from django.forms.fields import (
    ChoiceField,
    MultiValueField,
)

from django.forms.models import ModelChoiceField
from gbe.forms import ShowVoteWidget
from gbe.models import ShowVote


class ShowVoteField(MultiValueField):
    widget = ShowVoteWidget

    def __init__(self, *args, **kwargs):
        fields = [
            ModelChoiceField(
                queryset=[],
                empty_label="---------"),
            ChoiceField()]
        super(ShowVoteField, self).__init__(
            fields=fields,
            *args,
            **kwargs)

    def clean(self, value):
        if isinstance(value, ShowVote):
            return value
        raise Exception("failed in ShowVoteField.clean")
