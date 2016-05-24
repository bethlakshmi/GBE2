from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    PersonaFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    LocationFactory,
    OrderingFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
import pytz
from datetime import time
from datetime import datetime


class ShowContext:
    def __init__(self,
                 act=None,
                 performer=None,
                 conference=None,
                 room=None,
                 starttime=None,
                 day=None):
        self.performer = performer or PersonaFactory()
        self.conference = conference or ConferenceFactory()
        if not day:
            day = ConferenceDayFactory(conference=self.conference)
        self.days = [day]
        act = act or ActFactory(conference=self.conference,
                                performer=self.performer,
                                accepted=3)
        self.acts = [act]
        self.show = ShowFactory(conference=self.conference)
        self.room = room or RoomFactory()
        self.sched_event = None
        self.sched_event = self.schedule_instance(room=self.room,
                                                  starttime=starttime)
        self.book_act(act)

    def schedule_instance(self,
                          starttime=None,
                          room=None):
        room = room or self.room
        if starttime:
            sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr,
                                            starttime=starttime)
        elif self.sched_event:
            one_day = timedelta(1)
            sched_event = SchedEventFactory(
                eventitem=self.show.eventitem_ptr,
                starttime=self.sched_event.starttime+one_day)
        else:
            sched_event = SchedEventFactory(
                eventitem=self.show.eventitem_ptr,
                starttime=datetime.combine(
                    self.days[0].day,
                    time(12, 0, 0, tzinfo=pytz.utc)))
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        return sched_event

    def book_act(self, act=None):
        act = act or ActFactory(conference=self.conference,
                                accepted=3)
        booking = ResourceAllocationFactory(
            event=self.sched_event,
            resource=ActResourceFactory(_item=act))
        return (act, booking)

    def order_act(self, act, order):
        alloc=self.sched_event.resources_allocated.filter(
            resource__actresource___item=self.acts[0]).first()
        try:
            alloc.ordering = order
            alloc.ordering.save()
        except:
            OrderingFactory(allocation=alloc, order=order)
