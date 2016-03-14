import nose.tools as nt
from unittest import TestCase
from tests.factories.gbe_factories import ProfileFactory


class TestProfile(TestCase):
    def setUp(self):
        self.profile_factory = ProfileFactory

    def test_contact_phone(self):
        profile = self.profile_factory()
        assert profile.phone == profile.contact_phone

    def test_contact_email(self):
        profile = self.profile_factory()
        assert profile.user_object.email == profile.contact_email
