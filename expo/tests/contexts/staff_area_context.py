from tests.factories.gbe_factories import (
    GenericEventFactory,
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
class StaffAreaContext:
    '''
    Sets up a GenericEvent as a StaffArea in a pattern similar to what we
    create in practice - with some number of volunteer shifts and assigned
    volunteers in the shifts
    '''
    def __init__(self,
                 area=None,
                 staff_lead=None,
                 conference=None,
                 starttime=None):
        self.staff_lead = staff_lead or PersonaFactory()
        self.conference = conference or ConferenceFactory()
        self.area = area or GenericEventFactory(type='Staff Area',
                                              conference=self.conference)
        self.sched_event = None
        self.sched_event = self.schedule_instance(starttime=starttime)
        self.conf_day = ConferenceDayFactory(
            day=self.sched_event.starttime.date(),
            conference=self.conference)
        self.opportunities = None

    def schedule_instance(self,
                          starttime=None,
                          staff_lead=None):
        staff_lead = staff_lead or self.staff_lead
        if starttime:
            sched_event = SchedEventFactory(eventitem=self.area.eventitem_ptr,
                                            starttime=starttime)
        elif self.sched_event:
            one_day = timedelta(1)
            sched_event = SchedEventFactory(
                eventitem=self.area.eventitem_ptr,
                starttime=self.sched_event.starttime+one_day)
        else:
            sched_event = SchedEventFactory(eventitem=self.area.eventitem_ptr)
        ResourceAllocationFactory(
            event=sched_event,
            resource=WorkerFactory(_item=staff_lead.workeritem_ptr))
        return sched_event
