import factory
from factory import DjangoModelFactory
from factory import SubFactory, RelatedFactory
import scheduler.models as sched
from datetime import datetime
from django.utils import timezone
from tests.factories.gbe_factories import GenericEventFactory


class WorkerItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.WorkerItem


class SchedEventFactory(DjangoModelFactory):
    class Meta:
        model = sched.Event

    eventitem = SubFactory(GenericEventFactory)
    starttime = timezone.make_aware(datetime(2016, 02, 4),
                                    timezone.get_current_timezone())
