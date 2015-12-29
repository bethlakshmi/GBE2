from factory import (
    DjangoModelFactory,
    SubFactory,
    RelatedFactory,
    Sequence
)
import scheduler.models as sched
from datetime import datetime
from django.utils import timezone
from tests.factories.gbe_factories import GenericEventFactory

class SchedulableFactory(DjangoModelFactory):
    class Meta:
        model = sched.Schedulable


class ResourceItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.ResourceItem


class ResourceFactory(DjangoModelFactory):
    class Meta:
        model = sched.Resource


class ActItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.ActItem


class ActResourceFactory(DjangoModelFactory):
    _item = SubFactory(ActItemFactory)

    class Meta:
        model = sched.ActResource


class LocationItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.LocationItem


class LocationFactory(DjangoModelFactory):
    _item = SubFactory(LocationItemFactory)

    class Meta:
        model = sched.Location


class WorkerItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.WorkerItem


class WorkerFactory(DjangoModelFactory):
    _item = SubFactory(WorkerItemFactory)
    role = "Volunteer"

    class Meta:
        model = sched.Worker


class EquipmentItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.EquipmentItem


class EquipmentFactory(DjangoModelFactory):
    _item = SubFactory(EquipmentItemFactory)

    class Meta:
        model = sched.Equipment


class EventItemFactory(DjangoModelFactory):
    visible = True

    class Meta:
        model = sched.EventItem


class SchedEventFactory(DjangoModelFactory):
    eventitem = SubFactory(GenericEventFactory)
    starttime = timezone.make_aware(datetime(2015, 02, 4),
                                    timezone.get_current_timezone())
    max_volunteer = 0

    class Meta:
        model = sched.Event


class ResourceAllocationFactory(DjangoModelFactory):
    event = SubFactory(SchedEventFactory)
    resource = SubFactory(WorkerFactory)

    class Meta:
        model = sched.ResourceAllocation


class OrderingFactory(DjangoModelFactory):
    order = Sequence(lambda x: x)
    allocation = SubFactory(ResourceAllocationFactory)

    class Meta:
        model = sched.Ordering


class LabelFactory(DjangoModelFactory):
    text = Sequence(lambda x: "Label #%d" % x)
    allocation = SubFactory(ResourceAllocationFactory)

    class Meta:
        model = sched.Label


class EventContainerFactory(DjangoModelFactory):
    parent_event = SubFactory(SchedEventFactory)
    child_event = SubFactory(SchedEventFactory)

    class Meta:
        model = sched.EventContainer
