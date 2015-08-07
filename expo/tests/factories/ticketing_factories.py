import factory
from factory import DjangoModelFactory
from factory import SubFactory
import ticketing.models as tickets
import gbe.models as conf
from tests.factories import gbe_factories


class BrownPaperEventsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.BrownPaperEvents
    bpt_event_id = "111111"
    conference = SubFactory(gbe_factories.ConferenceFactory)
