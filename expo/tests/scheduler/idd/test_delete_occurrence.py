from django.test import (
    Client,
    TestCase
)
from scheduler.idd import delete_occurrence
from tests.contexts import VolunteerContext
from scheduler.models import ( 
    Event, 
    EventContainer, 
)


class TestDeleteOccurrence(TestCase):
    view_name = 'export_calendar'

    def setUp(self):
        self.client = Client()
        self.context = VolunteerContext()

    def test_delete_w_parent(self):
        response = delete_occurrence(self.context.sched_event.pk)
        self.assertEqual(response.warnings[0].code, "PARENT_EVENT_DELETION")
