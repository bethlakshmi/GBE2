import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from factories import UserFactory
from factories import ProfileFactory

    

class TestProfile(TestCase):
    def test_contact_phone(self):
        profile = ProfileFactory.create()
        assert profile.phone == profile.contact_phone
    
    def test_contact_email(self):
        profile = ProfileFactory.create()
        assert profile.user_object.email==profile.contact_email

    
        

