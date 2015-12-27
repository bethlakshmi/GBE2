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
    class Meta:
        model = sched.Event

    eventitem = SubFactory(GenericEventFactory)
    starttime = timezone.make_aware(datetime(2016, 02, 4),
                                    timezone.get_current_timezone())
    max_volunteer = 0

class ResourceAllocationFactory(DjangoModelFactory):
    class Meta:
        model = sched.ResourceAllocation

    event = SubFactory(SchedEventFactory)
    resource = SubFactory(WorkerFactory)


class OrderingFactory(DjangoModelFactory):
    class Meta:
        model = sched.Ordering

    order = Sequence(lambda x: x)
    allocation = SubFactory(ResourceAllocationFactory)


class LabelFactory(DjangoModelFactory):
    class Meta:
        model = sched.Label

    text = Sequence(lambda x: "Label #%d" %x)
    allocation = SubFactory(ResourceAllocationFactory)

class EventContainerFactory(DjangoModelFactory):
    class Meta:
        model = sched.EventContainer

    parent_event = SubFactory(SchedEventFactory)
    child_event = SubFactory(SchedEventFactory)
