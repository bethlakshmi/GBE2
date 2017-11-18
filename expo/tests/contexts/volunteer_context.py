from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    GenericEventFactory,
    ProfilePreferencesFactory,
    ProfileFactory,
    ShowFactory,
    VolunteerFactory,
    VolunteerWindowFactory,
    VolunteerInterestFactory
)
from tests.factories.scheduler_factories import (
    EventContainerFactory,
    EventLabelFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from datetime import (
    date,
    datetime,
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
        self.profile = profile or ProfileFactory()
        if not hasattr(self.profile, 'preferences'):
            ProfilePreferencesFactory(profile=self.profile)

        if bid is False:
            self.bid = None
        elif bid:
            self.bid = bid
            self.profile = self.bid.profile
        else:
            self.bid = VolunteerFactory(
                b_conference=self.conference,
                profile=self.profile)
        self.interest = VolunteerInterestFactory(
            volunteer=self.bid)
        self.opportunity = opportunity or GenericEventFactory(
            e_conference=self.conference,
            type='Volunteer',
            volunteer_type=self.interest.interest)
        self.event = event or ShowFactory(
            e_conference=self.conference)
        self.role = role or "Volunteer"
        self.sched_event = SchedEventFactory(
            eventitem=self.event.eventitem_ptr,
            starttime=datetime.combine(self.window.day.day,
                                       self.window.start))
        EventLabelFactory(event=self.sched_event,
                          text="General")
        EventLabelFactory(event=self.sched_event,
                          text=self.conference.conference_slug)
        self.opp_event = SchedEventFactory(
            eventitem=self.opportunity.eventitem_ptr,
            starttime=datetime.combine(self.window.day.day,
                                       self.window.start),
            max_volunteer=2)
        self.worker = WorkerFactory(_item=self.profile.workeritem,
                                    role=self.role)
        self.allocation = ResourceAllocationFactory(resource=self.worker,
                                                    event=self.opp_event)
        EventContainerFactory(parent_event=self.sched_event,
                              child_event=self.opp_event)
        EventLabelFactory(event=self.opp_event,
                          text=self.conference.conference_slug)
        EventLabelFactory(event=self.opp_event,
                          text="Volunteer")

    def add_window(self):
        add_window = VolunteerWindowFactory(
            day=ConferenceDayFactory(
                conference=self.conference,
                day=date(2016, 2, 6)))
        return add_window
