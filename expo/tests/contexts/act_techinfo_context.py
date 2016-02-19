from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
    CueInfoFactory,
    PersonaFactory,
    RoomFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
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
                 cue_count=1):
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
        sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr)
        room_name = room_name or "Dining Room"
        self.room = RoomFactory(name=room_name)
        ResourceAllocationFactory(
            event=sched_event,
            resource=LocationFactory(_item=self.room.locationitem_ptr))
                # schedule the act into the show
        ResourceAllocationFactory(
            event=sched_event,
            resource=ActResourceFactory(_item=self.act.actitem_ptr))
