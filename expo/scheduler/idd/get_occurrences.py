from scheduler.models import (
    Event,
)
from scheduler.data_transfer import (
    Error,
    OccurrencesResponse
)
from datetime import (
    datetime,
    time
)


def get_occurrences(parent_event_id=None,
                    labels=[],
                    day=None,
                    foreign_event_ids=None,
                    max_volunteer=None):
    response = OccurrencesResponse()
    filter_occurrences = Event.objects.all()

    if foreign_event_ids:
        filter_occurrences = filter_occurrences.filter(
            eventitem__eventitem_id__in=foreign_event_ids
        )
    if parent_event_id:
        filter_occurrences = filter_occurrences.filter(
            container_event__parent_event__pk=parent_event_id)
    for label in labels:
        filter_occurrences = filter_occurrences.filter(
            eventlabel__text=label
        )
    if max_volunteer is not None:
        filter_occurrences = filter_occurrences.filter(
            max_volunteer__gte=max_volunteer)
    if day:
        filter_occurrences = filter_occurrences.filter(
            starttime__range=(
                datetime.combine(day, time(0, 0, 0, 0)),
                datetime.combine(day, time(23, 59, 59, 999999)))
        )

    response.occurrences = filter_occurrences.order_by('starttime')
    return response
