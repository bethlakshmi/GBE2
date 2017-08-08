from scheduler.models import (
    Event,
    EventContainer,
    EventItem,
    EventLabel,
)
from scheduler.data_transfer import OccurrenceResponse


def create_occurrence(event_id,
                      start_time,
                      max_volunteer=0,
                      people=[],
                      locations=[],
                      parent_event=None,
                      labels=[]):
    response = OccurrenceResponse()
    response.occurrence = Event(
        eventitem=EventItem.objects.get(eventitem_id=event_id),
        starttime=start_time,
        max_volunteer=max_volunteer)
    response.occurrence.save()
    if len(locations) > 0:
        response.occurrence.set_locations(locations)

    for person in people:
        response.warnings += response.occurrence.allocate_person(person)

    for label in labels:
        response.occurrence.add_label(label)

    if parent_event:
        family = EventContainer(
            parent_event=parent_event,
            child_event=response.occurrence)
        family.save()

    return response
