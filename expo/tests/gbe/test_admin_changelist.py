from django.test import (
    Client,
    TestCase
)
from django.test.client import RequestFactory
from django.contrib.admin.views.main import ALL_VAR, SEARCH_VAR, ChangeList
from gbe.admin import (
    EventAdmin,
    VolunteerInterestAdmin,
    VolunteerWindowAdmin,
)
from gbe.models import (
    Event,
    VolunteerInterest,
    VolunteerWindow,
)
from tests.factories.gbe_factories import(
    GenericEventFactory,
    ProfileFactory,
    UserFactory,
    VolunteerInterestFactory,
    VolunteerWindowFactory,
)
from django.contrib.admin.sites import AdminSite
from tests.functions.gbe_functions import login_as


class GBEChangeListTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.privileged_user = ProfileFactory()
        self.privileged_user.user_object.is_superuser = True
        self.privileged_user.user_object.save()

    def test_get_volunteer_interest_conference(self):
        obj = VolunteerInterestFactory()
        m = VolunteerInterestAdmin(VolunteerInterest, AdminSite)
        login_as(self.privileged_user, self)
        response = self.client.get('/admin/gbe/volunteerinterest/')
        print response.content
        assert str(obj.volunteer.conference) in response.content

    def test_get_volunteer_window_conference(self):
        obj = VolunteerWindowFactory()
        m = VolunteerWindowAdmin(VolunteerWindow, AdminSite)
        login_as(self.privileged_user, self)
        response = self.client.get('/admin/gbe/volunteerwindow/')
        print response.content
        assert str(obj.day.conference) in response.content
