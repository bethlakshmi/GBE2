from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory
)


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
