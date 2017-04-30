from django.shortcuts import get_object_or_404
    
from scheduler.models import (
    Event,
    EventContainer,
    EventItem,
    WorkerItem,
)

def create_scheduled_event(
        event_id,
        start_time,
        max_volunteer=0,
        parent_sched_id=None,
        people=[],
        locations=[],
        labels=[]):
    warnings = []
    errors = []

    eventitem = get_object_or_404(EventItem, pk=event_id)
    event = Event(eventitem=eventitem,
                  starttime=start_time,
                  max_volunteer=max_volunteer)
    
    if parent_sched_id:
        parent = get_object_or_404(Event, pk=parent_sched_id)
        EventContainer(parent=parent, child=event)

    loc_details = []
    for location in locations:
        success = event.set_location(location)
        if not success:
            loc_details += [location]
            
    if len(loc_details) > 0:
        errors += [{
            'code': "LOCATION_ADD_FAILED",
            'details': details}]

    for person in people:
        if 'public_id' in person:
            worker = get_object_or_404(WorkerItem, pk=person['public_id'])
        else:
            worker = person['user'].profile
        warnings += [event.allocate_worker(
            worker,
            person['role'],
            person['label'])]

    for label in labels:
        new_label = event.add_label(label)
        if not new_label:
            errors += "EVENT_LABEL_CREATE_FAILURE"
    
