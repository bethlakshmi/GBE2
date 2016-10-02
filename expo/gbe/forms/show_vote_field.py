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

    def get_prep_value(self, value):
        if isinstance(value, ShowVote):
            return value
        return ShowVote.objects.get(pk=value)

    def clean(self, value):
        if isinstance(value, ShowVote):
            return value
        raise Exception("failed in ShowVoteField.clean")

    def compress(self, data_list):
        if data_list:
            if any([datum in self.empty_values for datum in data_list]):
                raise ValidationError()
            return ShowVote(show_pk=data_list[0],
                            vote=data_list[1])
        return None
