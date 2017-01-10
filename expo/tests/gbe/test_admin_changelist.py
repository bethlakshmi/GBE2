from django.test import TestCase
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
    VolunteerInterestFactory,
    VolunteerWindowFactory,
)
from django.contrib.admin.sites import AdminSite


class GBEChangeListTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_select_volunteer_interest_conference(self):
        obj = VolunteerInterestFactory()
        m = VolunteerInterestAdmin(VolunteerInterest, AdminSite)
        request = self.factory.get('/volunteerinterest/')
        cl = ChangeList(
            request, VolunteerInterest,
            *get_changelist_args(m, list_select_related=m.get_list_select_related(request))
        )
        self.assertEqual(cl.queryset.query.select_related, {'parent': {}})
