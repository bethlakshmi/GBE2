from tests.factories.gbe_factories import (
    GenericEventFactory,
    ProfileFactory,
    ShowFactory,
    VolunteerFactory,
    VolunteerWindowFactory,
)
from tests.factories.scheduler_factories import (
    EventContainerFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)


class VolunteerContext():
    def __init__(self,
                 profile=None,
                 bid=None,
                 event=None,
                 opportunity=None,
                 role=None):
        self.window = VolunteerWindowFactory()
        self.conference = self.window.day.conference
        if bid is False:
            self.profile = profile or ProfileFactory()
            self.bid = None
        elif bid:
            self.bid = bid
            self.profile = self.bid.profile
        else:
            self.bid = VolunteerFactory(
                b_conference=self.conference)
            self.profile = self.bid.profile
        self.opportunity = opportunity or GenericEventFactory()
        self.event = event or ShowFactory()
        self.role = role or "Volunteer"
        self.sched_event = SchedEventFactory(
            eventitem=self.event.eventitem_ptr)
        self.opp_event = SchedEventFactory(
            eventitem=self.opportunity.eventitem_ptr)
        self.worker = WorkerFactory(_item=self.profile.workeritem,
                                    role=self.role)
        self.allocation = ResourceAllocationFactory(resource=self.worker,
                                                    event=self.sched_event)
        EventContainerFactory(parent_event=self.sched_event,
                              child_event=self.opp_event)
