from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    CueInfoFactory,
    GenericEventFactory,
    PersonaFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    EventContainerFactory,
    LocationFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)


class ActTechInfoContext():
    def __init__(self,
                 performer=None,
                 act=None,
                 show=None,
                 conference=None,
                 room_name=None,
                 cue_count=1,
                 schedule_rehearsal=False):
        self.conference = conference or ConferenceFactory()
        self.performer = performer or PersonaFactory()
        self.act = act or ActFactory(performer=self.performer,
                                     conference=self.conference,
                                     accepted=3)
        self.tech = self.act.tech
        self.audio = self.tech.audio
        self.lighting = self.tech.lighting
        self.stage = self.tech.stage
        for i in range(cue_count):
            CueInfoFactory.create(techinfo=self.tech,
                                  cue_sequence=i)
        self.show = show or ShowFactory(conference=self.conference)
        # schedule the show
        self.sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr)
        room_name = room_name or "Dining Room"
        self.room = RoomFactory(name=room_name)
        ResourceAllocationFactory(
            event=self.sched_event,
            resource=LocationFactory(_item=self.room.locationitem_ptr))
        # schedule the act into the show
        ResourceAllocationFactory(
            event=self.sched_event,
            resource=ActResourceFactory(_item=self.act.actitem_ptr))
        if schedule_rehearsal:
            self.rehearsal = _schedule_rehearsal(self.sched_event, self.act)


def _schedule_rehearsal(s_event, act):
    rehearsal = GenericEventFactory(type="Rehearsal Slot")
    rehearsal_event = SchedEventFactory(eventitem=rehearsal.eventitem_ptr,
                                        max_volunteer=10)
    event_container = EventContainerFactory(
        child_event=rehearsal_event,
        parent_event=s_event)
    ResourceAllocationFactory(resource=ActResourceFactory(
        _item=act.actitem_ptr),
                              event=s_event)
    return rehearsal_event
