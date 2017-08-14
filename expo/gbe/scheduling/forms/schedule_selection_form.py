from django.forms import (
    ModelChoiceField,
    ModelMultipleChoiceField,
)
from gbe.models import (
    Event,
)
from gbe_forms_text import (
    scheduling_help_texts,
    scheduling_labels,
)
from gbe.forms.common_queries import (
    visible_personas,
    visible_profiles,
)
from gbe.scheduling.forms import ScheduleBasicForm


class ScheduleSelectionForm(ScheduleBasicForm):
    teacher = ModelChoiceField(
        queryset=visible_personas,
        required=False)
    moderator = ModelChoiceField(
        queryset=visible_personas,
        required=False)
    panelists = ModelMultipleChoiceField(
        queryset=visible_personas,
        required=False)
    staff_lead = ModelChoiceField(
        queryset=visible_profiles,
        required=False)

    class Meta:
        model = Event
        fields = ['e_title', 'e_description', 'duration']
        help_texts = scheduling_help_texts
        labels = scheduling_labels
