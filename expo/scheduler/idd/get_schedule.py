from scheduler.data_transfer import (
    Error,
    ScheduleResponse,
    ScheduleItem,
)


# DEPRECATE - not really deprecate, but totally rework when model
# refactor is done.  It bounces across apps hideously
def get_schedule(user=None, labels=[]):
    response = ScheduleResponse()
    old_schedule = user.profile.get_schedule_as_bookings(labels)
    for item in old_schedule:
        booking_label = None
        if hasattr(item, 'label'):
            booking_label = item.label
        response.schedule_items += [ScheduleItem(
            user=user,
            event=item.event,
            role=item.resource.as_subtype.role,
            label=booking_label)]
    return response
