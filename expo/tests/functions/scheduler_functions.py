from tests.factories.scheduler_factories import (
    ActResourceFactory,
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

def book_act_item_for_show(actitem, eventitem):
        booking = ResourceAllocationFactory.create(
            event=SchedEventFactory.create(
                eventitem=eventitem),
            resource=ActResourceFactory.create(
            _item=actitem)
        )
        return booking
