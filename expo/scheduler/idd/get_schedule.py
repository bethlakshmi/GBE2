from scheduler.data_transfer import (
    Error,
    ScheduleResponse,
    ScheduleItem,
)
from scheduler.models import ResourceAllocation


# DEPRECATE - not really deprecate, but totally rework when model
# refactor is done.  It bounces across apps hideously
def get_schedule(user=None, labels=[]):
    bookable_items = user.profile.get_bookable_items()
    basic_filter = ResourceAllocation.objects.all()
    sched_items = []
    if len(labels) > 0:
        basic_filter = basic_filter.filter(
                event__eventlabel__text__in=labels)
    if len(bookable_items['acts']) > 0:
        for item in basic_filter.filter(
                resource__actresource___item__in=bookable_items['acts']):
            booking_label = None
            if hasattr(item, 'label'):
                booking_label = item.label
            sched_items += [ScheduleItem(
                user=user,
                event=item.event,
                role="Performer",
                label=booking_label)]
    if len(bookable_items['performers']) > 0:
        for item in basic_filter.filter(
                resource__worker___item__in=bookable_items['performers']):
            booking_label = None
            if hasattr(item, 'label'):
                booking_label = item.label
            sched_items += [ScheduleItem(
                user=user,
                event=item.event,
                role=item.resource.as_subtype.role,
                label=booking_label)]
    for item in basic_filter.filter(
            resource__worker___item=user.profile):
        booking_label = None
        if hasattr(item, 'label'):
            booking_label = item.label
        sched_items += [ScheduleItem(
            user=user,
            event=item.event,
            role=item.resource.as_subtype.role,
            label=booking_label)]
    response = ScheduleResponse(
        schedule_items=sorted(
            set(sched_items),
            key=lambda sched_items: sched_items.event.start_time))
    return response
