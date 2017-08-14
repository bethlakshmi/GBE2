from django.forms import (
    HiddenInput,
    IntegerField,
    ModelChoiceField,
)
from gbe.models import (
    AvailableInterest,
    GenericEvent,
)

class VolunteerOpportunityForm(ScheduleBasicForm):
    opp_event_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    opp_sched_id = IntegerField(
        widget=HiddenInput(),
        required=False)
    duration = DurationFormField(
        error_messages={'null': 'required'})
    volunteer_type = ModelChoiceField(
        queryset=AvailableInterest.objects.filter(visible=True),
        required=False)

    class Meta:
        model = GenericEvent
        fields = ['e_title',
                  'volunteer_type',
                  'num_volunteers',
                  'duration',
                  'day',
                  'time',
                  'location',
                  ]
        hidden_fields = ['opp_event_id']
