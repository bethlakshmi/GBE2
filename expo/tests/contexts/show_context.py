from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    EventLabelFactory,
    LocationFactory,
    OrderingFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
import pytz
from tests.functions.scheduler_functions import noon
from datetime import (
    timedelta,
)


class ShowContext:
    def __init__(self,
                 act=None,
                 performer=None,
                 conference=None,
                 room=None,
                 starttime=None,
                 act_role=''):
        self.performer = performer or PersonaFactory()
        self.conference = conference or ConferenceFactory()
        if not self.conference.conferenceday_set.exists():
            day = ConferenceDayFactory(conference=self.conference)
            if starttime:
                day.day = starttime.date()
                day.save()
        self.days = self.conference.conferenceday_set.all()
        act = act or ActFactory(b_conference=self.conference,
                                performer=self.performer,
                                accepted=3,
                                submitted=True)
        self.acts = [act]
        self.show = ShowFactory(e_conference=self.conference)
        self.room = room or RoomFactory()
        self.sched_event = None
        self.sched_event = self.schedule_instance(room=self.room,
                                                  starttime=starttime)
        self.book_act(act, act_role)

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
                starttime=noon(self.days[0]))
        EventLabelFactory(event=sched_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=sched_event,
                          text="General")
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=room.locationitem_ptr))
        return sched_event

    def book_act(self, act=None, act_role=''):
        act = act or ActFactory(b_conference=self.conference,
                                accepted=3,
                                submitted=True)
        booking = ResourceAllocationFactory(
            event=self.sched_event,
            resource=ActResourceFactory(_item=act, role=act_role))
        return (act, booking)

    def order_act(self, act, order):
        alloc = self.sched_event.resources_allocated.filter(
            resource__actresource___item=self.acts[0]).first()
        try:
            alloc.ordering = order
            alloc.ordering.save()
        except:
            OrderingFactory(allocation=alloc, order=order)

    def set_interest(self, interested_profile=None):
        interested_profile = interested_profile or ProfileFactory()
        ResourceAllocationFactory(event=self.sched_event,
                                  resource=WorkerFactory(
                                    _item=interested_profile,
                                    role="Interested"))
        return interested_profile
