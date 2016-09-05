from django.forms.fields import (
    ChoiceField,
    MultiValueField,
)

from django.forms.models import ModelChoiceField
from gbe.forms import ShowVoteWidget
from gbe.functions import get_current_conference
from gbe.models import (
    Show,
    ShowVote,
)
from gbetext import vote_options

class ShowVoteField(MultiValueField):
    widget = ShowVoteWidget
    def __init__(self, *args, **kwargs):
        fields = (
            ModelChoiceField(
                queryset=Show.objects.filter(
                    conference=get_current_conference()),
                empty_label="---------"),
            ChoiceField(choices=vote_options))
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
