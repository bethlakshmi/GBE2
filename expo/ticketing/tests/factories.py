import factory
from factory import DjangoModelFactory
from factory import SubFactory
import ticketing.models as tickets
import gbe.models as conf

# I'd be glad to reuse, but I can't import gbe.tests.factories into
# the ticketing test module?
class UserFactory(DjangoModelFactory):
    class Meta:
        model = conf.User
    first_name = factory.Sequence(lambda n: 'John_%d' % n)
    last_name = 'Smith'
    username = factory.LazyAttribute(lambda a: "%s" % (a.first_name))
    email = '%s@smith.com' % username

class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = conf.Profile
    user_object = SubFactory(UserFactory)
    address1 = '123 Main St.'
    address2 = factory.Sequence(lambda n: 'Apt. %d' % n)
    city = 'Smithville'
    state = 'MD'
    zip_code = '12345'
    country = 'USA'
    phone = '617-282-9268'
    display_name=factory.LazyAttribute(lambda a: "%s_%s"%(a.user_object.first_name, 
                                                          a.user_object.last_name))

class BrownPaperEventsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.BrownPaperEvents
    bpt_event_id = "111111"

