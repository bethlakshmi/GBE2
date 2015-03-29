import factory
import gbe.models as conf

class UserFactory(factory.Factory):
    class Meta:
        model = conf.User

    first_name = 'John'
    last_name = 'Smith'
    email = 'john.smith@smith.com'


class ProfileFactory(factory.Factory):
    class Meta:
        model = conf.Profile
    
    user_object = UserFactory.create()
    user_object.save()
    address1 = '123 Main St.'
    address2 = 'Apt. 3'
    city = 'Smithville'
    state = 'MD'
    zip_code = '12345'
    country = 'USA'
    phone = '617-282-9268'
