from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceFactory,
    PersonaFactory,
    RoomFactory,
)
from tests.factories.scheduler_factories import (
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)


class ClassContext:
    def __init__(self,
                 bid=None,
                 teacher=None,
                 conference=None,
                 room=None,
                 starttime=None):
        self.teacher = teacher or PersonaFactory()
        self.bid = bid or ClassFactory()
        self.conference = conference or ConferenceFactory()
        self.room = room or RoomFactory()
        self.sched_event = None
        self.sched_event = self.schedule_instance(room=self.room,
                                                  starttime=starttime)

    def schedule_instance(self,
                          starttime=None,
                          room=None,
                          teacher=None):
        room = room or self.room
        teacher = teacher or self.teacher
        if starttime:
            sched_event = SchedEventFactory(eventitem=self.bid.eventitem_ptr,
                                            starttime=starttime)
        elif self.sched_event:
            one_day = timedelta(1)
            sched_event = SchedEventFactory(
                eventitem=self.bid.eventitem_ptr,
                starttime=self.sched_event.starttime+one_day)
        else:
            sched_event = SchedEventFactory(eventitem=self.bid.eventitem_ptr)
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        ResourceAllocationFactory(
            event=sched_event,
            resource=WorkerFactory(_item=teacher.workeritem_ptr))
        return sched_event
