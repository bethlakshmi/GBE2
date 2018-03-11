from django.forms import (
    CharField,
    HiddenInput,
    IntegerField,
)
from gbe.models import GenericEvent
from gbe.scheduling.forms import ScheduleBasicForm


class RehearsalSlotForm(ScheduleBasicForm):
    opp_event_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    opp_sched_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    type = CharField(
        widget=HiddenInput(),
        required=True,
        initial="Rehearsal Slot")

    class Meta:
        model = GenericEvent
        fields = ['e_title',
                  'max_volunteer',
                  'duration',
                  'day',
                  'time',
                  'location',
                  'type',
                  ]
        hidden_fields = ['opp_event_id', 'e_description']
