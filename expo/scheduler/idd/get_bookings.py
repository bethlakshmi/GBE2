from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    Error,
    PeopleResponse,
    Person,
)


def get_bookings(occurrence_ids, role=None):
    people = []
    bookings = ResourceAllocation.objects.filter(event__pk__in=occurrence_ids)
    if role:
        bookings = bookings.filter(resource__worker__role=role)
    for booking in bookings:
        if booking.resource.as_subtype.__class__.__name__ == "Worker":
            person = Person(
                booking_id=booking.pk,
                worker=booking.resource.worker,
                role=booking.resource.worker.role,
                )
            if hasattr(booking, 'label'):
                person.label = booking.label.text
            people += [person]
    return PeopleResponse(people=people)
