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

    def test_delete_w_parent(self):
        response = delete_occurrence(self.context.sched_event.pk)
        self.assertEqual(response.warnings[0].code, "PARENT_EVENT_DELETION")

    def test_delete_bad_occurrence(self):
        event = Event.objects.filter(pk=(self.context.opp_event.pk+1000))
        response = delete_occurrence(self.context.opp_event.pk+1000)
        self.assertEqual(response.errors[0].code, "OCCURRENCE_NOT_FOUND")
