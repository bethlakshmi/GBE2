from scheduler.models import (
    Label,
    ResourceAllocation,
)
from scheduler.data_transfer import (
    Error,
    PeopleResponse,
    Person,
)


def get_bookings(occurrence_id):
    response = PersonResponse()
    bookings = ResourceAllocation.objects.filter(event__pk=occurrence_id)
    for booking in bookings:
        person = Person(
                booking_id=booking.pk,
                user=data['worker'].workeritem.as_subtype.user_object,
                public_id=data['worker'].workeritem.as_subtype.pk,
                role=data['role'])
        if hasattr(Label, booking):
            person.label = booking.label
    return response
