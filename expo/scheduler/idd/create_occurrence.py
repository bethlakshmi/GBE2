from scheduler.models import (
    Event,
    EventContainer,
    EventItem,
    EventLabel,
)
from scheduler.idd import OccurrenceResponse


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
    for l in locations:
        success = response.occurrence.set_location(l)
        if not success:
            response.add_error(
                'LOCATION_SET_FAILURE',
                'Could not find %s' % str(location))

    for person in people:
        response.warnings = response.occurrence.allocate_person(person)

    for label in labels:
        event_label = EventLabel(event=response.occurrence, text=label)
        event_label.save()

    if parent_event:
        family = EventContainer(
            parent_event=parent_event,
            child_event=response.occurrence)
        family.save()

    return response
