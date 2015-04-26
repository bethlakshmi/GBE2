import factory
from factory import DjangoModelFactory
from factory import SubFactory
import gbe.models as conf
import scheduler.models as sched

class WorkerItemFactory(DjangoModelFactory):
    class Meta:
        model= sched.WorkerItem
    


class UserFactory(DjangoModelFactory):
    class Meta:
        model = conf.User
    first_name = factory.Sequence(lambda n: 'John_%d' % n)
    last_name = 'Smith'
    username = factory.LazyAttribute(lambda obj:'%s@smith.com' % obj.first_name) 
    email = '%s@smith.com' %username

    
class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = conf.Profile
    user_object = SubFactory(UserFactory)
    address1 = '123 Main St.'
    address2 = factory.Sequence(lambda n: 'Apt. %d' %n)
    city = 'Smithville'
    state = 'MD'
    zip_code = '12345'
    country = 'USA'
    phone = '617-282-9268'
    display_name='Foo Bar'
    


