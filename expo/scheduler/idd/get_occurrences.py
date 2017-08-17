from scheduler.models import (
    Event,
)
from scheduler.data_transfer import (
    Error,
    OccurrencesResponse
)


def get_occurrences(parent_event_id=None):
    response = OccurrencesResponse()
    
    if parent_event_id:
        response.occurrences = Event.objects.filter(
            container_event__parent_event__pk=parent_event_id)

    return response
