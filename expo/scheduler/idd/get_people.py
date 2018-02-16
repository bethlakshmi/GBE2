from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def get_people(labels=[], roles=[]):
    if len(labels) == 0 and len(roles) == 0:
        return PeopleResponse(
            errors=[Error(
                code="INVALID_REQUEST",
                details="Either a label or a role must be provided."), ])
    people = []
    bookings = ResourceAllocation.objects.all()
    if len(labels) > 0:
        bookings = bookings.filter(event__eventlabel__text__in=labels)
    if "Performer" in roles:
        act_bookings = bookings.filter(resource__actresource__pk__gt=0)
    if len(roles) > 0:
        bookings = bookings.filter(resource__worker__role__in=roles)
    if len(labels) > 0:
        bookings = bookings.filter(event__eventlabel__text__in=labels)
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
    for booking in act_bookings:
        if booking.resource.as_subtype.__class__.__name__ == "ActResource":
            performer = booking.resource.actresource.item.as_subtype.performer
            person = Person(
                booking_id=booking.pk,
                user=performer.user_object,
                role="Performer",
                public_class=performer.__class__.__name__,
                public_id=performer.pk
                )
            if hasattr(booking, 'label'):
                person.label = booking.label.text
            people += [person]
    return PeopleResponse(people=people)
