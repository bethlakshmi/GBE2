from random import randint
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

from gbe.models import Class
import pytz
from datetime import (
    datetime,
    time,
    timedelta,
)


def unique_string(base_string):
    return base_string % str(randint(0, 10000))


def noon(day):
    return datetime.combine(day.day,
                            time(12, 0, 0, tzinfo=pytz.utc))


class ClassContext:
    def __init__(self,
                 bid=None,
                 teacher=None,
                 conference=None,
                 room=None,
                 starttime=None):
        self.teacher = teacher or PersonaFactory()
        self.conference = conference or ConferenceFactory()
        if not self.conference.conferenceday_set.exists():
            ConferenceDayFactory(conference=self.conference)
        self.days = self.conference.conferenceday_set.all()
        self.starttime = starttime or noon(self.days[0])
        self.bid = bid or ClassFactory(conference=self.conference,
                                       accepted=3,
                                       teacher=self.teacher)
        self.bid.title = unique_string("Class Title %s")
        self.bid.eventitem_ptr.title = self.bid.title
        self.bid.biddable_ptr.title = self.bid.title
        self.bid.save()
        self.bid.eventitem_ptr.save()
        self.bid.biddable_ptr.save()
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
                starttime=noon(self.days[0]))
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        ResourceAllocationFactory(
            event=sched_event,
            resource=WorkerFactory(_item=teacher.workeritem_ptr,
                                   role='Teacher'))
        return sched_event
