from django.test import (
    Client,
    TestCase
)
from scheduler.idd import delete_occurrence
from tests.contexts import VolunteerContext


class TestDeleteOccurrence(TestCase):
    view_name = 'export_calendar'

    def setUp(self):
        self.client = Client()
        self.context = VolunteerContext()

    def test_delete_bad_occurrence(self):
        response = delete_occurrence(self.context.opp_event.pk+1000)
        self.assertEqual(response.errors[0].code, "OCCURRENCE_NOT_FOUND")
