from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceDayFactory,
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
import pytz
from datetime import time
from datetime import datetime


class ClassContext:
    def __init__(self,
                 bid=None,
                 teacher=None,
                 conference=None,
                 room=None,
                 starttime=None,
                 day=None):
        self.teacher = teacher or PersonaFactory()
        self.conference = conference or ConferenceFactory()
        if not day:
            day = ConferenceDayFactory(conference=self.conference)
        self.days = [day]
        self.bid = bid or ClassFactory(conference=self.conference,
                                       accepted=3)
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
            sched_event = SchedEventFactory(
                eventitem=self.bid.eventitem_ptr,
                starttime=datetime.combine(
                    self.days[0].day,
                    time(12, 0, 0, tzinfo=pytz.utc)))
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        ResourceAllocationFactory(
            event=sched_event,
            resource=WorkerFactory(_item=teacher.workeritem_ptr,
                                   role='Teacher'))
        return sched_event
