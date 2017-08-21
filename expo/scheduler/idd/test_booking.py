from scheduler.models import (
    ResourceAllocation,
)


def test_booking(booking_id, occurrence_id=None):
    response = False
    if occurrence_id:
        response = ResourceAllocation.objects.filter(
            pk=booking_id,
            event__pk=occurrence_id).exists()
    else:
        response = ResourceAllocation.objects.filter(
            pk=booking_id).exists()
    return response
