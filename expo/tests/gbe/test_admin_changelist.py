from django.test import TestCase, ignore_warnings, override_settings
from django.test.client import RequestFactory
from django.contrib.admin.views.main import ALL_VAR, SEARCH_VAR, ChangeList
from gbe.admin import (
    EventAdmin,
    VolunteerInterestAdmin,
    VolunteerWindowAdmin,
    site as custom_site,
)
from gbe.models import (
    Event,
    VolunteerInterest,
    VolunteerWindow,
)
from factories.gbe_factories import (
    GenericEventFactory,
    VolunteerInterestFactory,
    VolunteerWindowFactory,
)


class GBEChangeListTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_select_volunteer_interest_conference(self):
        obj = VolunteerInterestFactory()
        m = VolunteerInterestAdmin(VolunteerInterest, custom_site)
        request = self.factory.get('/volunteerinterest/')
        cl = ChangeList(
            request, VolunteerInterest,
            *get_changelist_args(m, list_select_related=m.get_list_select_related(request))
        )
        self.assertEqual(cl.queryset.query.select_related, {'parent': {}})
