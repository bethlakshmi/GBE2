from scheduler.models import (
    Event,
    EventContainer,
    EventLabel,
    Worker,
)
from scheduler.data_transfer import OccurrenceResponse
from scheduler.idd import get_occurrence


def update_occurrence(occurrence_id,
                      start_time=None,
                      max_volunteer=None,
                      people=None,
                      locations=None,
                      parent_event_id=None,
                      labels=None):
    response = get_occurrence(occurrence_id)
    if response.errors:
        return response

    if parent_event_id and parent_event_id > -1:
        parent_response = get_occurrence(parent_event_id)
        if parent_response.errors:
            return parent_response

    if start_time:
        response.occurrence.starttime = start_time
    if max_volunteer:
        response.occurrence.max_volunteer = max_volunteer
    if start_time or max_volunteer:
        response.occurrence.save()

    if locations is not None:
        response.occurrence.set_locations(locations)

    if people is not None:
        Worker.objects.filter(allocations__event=response.occurrence).delete()
        for person in people:
            response.warnings += response.occurrence.allocate_person(person)

    if labels is not None:
        if EventLabel.objects.filter(event=response.occurrence).exists():
            EventLabel.objects.filter(event=response.occurrence).delete()
        for label in labels:
            response.occurrence.add_label(label)

    if parent_event_id:
        if parent_event_id > -1:
            family = EventContainer(
                parent_event=parent_response.occurrence,
                child_event=response.occurrence)
            family.save()
        # -1 means "delete all parents"
        elif EventContainer.objects.filter(
                child_event=response.occurrence).exists():
            EventContainer.objects.filter(child_event=response.occurrence).delete()

    return response
