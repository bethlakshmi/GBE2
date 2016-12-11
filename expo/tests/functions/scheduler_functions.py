from tests.factories.scheduler_factories import (
    ActResourceFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory
)
from datetime import (
    datetime,
    time
)
import pytz


def book_worker_item_for_role(workeritem, role, eventitem=None):
        worker = WorkerFactory.create(
            _item=workeritem,
            role=role)
        if eventitem:
            event = SchedEventFactory.create(
                eventitem=eventitem)
        else:
            event = SchedEventFactory.create()

        booking = ResourceAllocationFactory.create(
            event=event,
            resource=worker
        )
        return booking


def book_act_item_for_show(actitem, eventitem):
        booking = ResourceAllocationFactory.create(
            event=SchedEventFactory.create(
                eventitem=eventitem),
            resource=ActResourceFactory.create(
                _item=actitem))
        return booking


def get_sched_event_form(context, room=None):
    room = room or context.room
    form_dict = {'event-day': context.days[0].pk,
                 'event-time': "12:00:00",
                 'event-location': room.pk,
                 'event-max_volunteer': 3,
                 'event-title': 'New Title',
                 'event-duration': '1:00:00',
                 'event-description': 'New Description'}
    return form_dict


def assert_good_sched_event_form(response, eventitem):
    assert response.status_code is 200
    assert eventitem.title in response.content
    assert eventitem.description in response.content
    assert '<input id="id_event-duration" name="event-duration" ' + \
        'type="text" value="01:00:00" />' in response.content


def noon(day):
    return datetime.combine(day.day,
                            time(12, 0, 0, tzinfo=pytz.utc))


def assert_selected(response, value, display):
    selection = '<option value="%s" selected="selected">%s</option>' % (
        value,
        display)
    assert selection in response.content


def assert_link(response, link):
    selection = '<a href="%s">' % link
    assert selection in response.content
