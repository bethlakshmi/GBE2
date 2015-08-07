from tests.factories import gbe_factories as factories
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase

class TestProfile(TestCase):
    def setUp(self):
        self.profile_factory = factories.ProfileFactory

    def test_contact_phone(self):
#        import pdb;pdb.set_trace()
        profile = self.profile_factory.create()
        assert profile.phone == profile.contact_phone
    
    def test_contact_email(self):
        profile = self.profile_factory.create()
        assert profile.user_object.email==profile.contact_email

    
        

