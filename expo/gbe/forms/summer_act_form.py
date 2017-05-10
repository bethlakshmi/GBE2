from django.forms import (
    CheckboxSelectMultiple,
    MultipleChoiceField,
)
from gbe.forms import (
    ActEditDraftForm,
    ActEditForm,
)
from gbe_forms_text import (
    act_help_texts,
    act_bid_labels,
    also_consider_act_for,
)
from gbetext import (
    act_shows_options,
)
from gbe.functions import get_current_conference


class SummerActDraftForm(ActEditDraftForm):
    shows_preferences = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=act_shows_options,
        label=act_bid_labels['summer_shows_preferences'],
        help_text=act_help_texts['shows_preferences'],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(SummerActDraftForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            conference = kwargs.pop('instance').b_conference
        else:
            conference = get_current_conference()

        summer_options = []
        for day in conference.conferenceday_set.all():
            summer_options += [(day.pk, day)]
        
        summer_options += [(-1, also_consider_act_for)]
        self.fields['shows_preferences'].choices = summer_options


class SummerActForm(SummerActDraftForm):
    shows_preferences = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=act_shows_options,
        label=act_bid_labels['summer_shows_preferences'],
        help_text=act_help_texts['shows_preferences']
    )
