from django.test import TestCase
from scheduler.idd import get_occurrences


class TestGetOccurrences(TestCase):
    view_name = 'export_calendar'

    def test_get_labels_and_label_sets(self):
        response = get_occurrences(labels=["foo"], label_sets=["bar"],)
        self.assertEqual(response.errors[0].code, "INVALID_REQUEST")
