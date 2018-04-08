from django.test import TestCase
from scheduler.idd import get_eval_info
from tests.factories.scheduler_factories import EventEvalQuestionFactory
from scheduler.models import EventEvalQuestion


class TestGetEvalInfo(TestCase):
    view_name = 'export_calendar'

    def setUp(self):
        EventEvalQuestion.objects.all().delete()
        self.question = EventEvalQuestionFactory(visible=False)

    def test_get_person_w_label(self):
        response = get_eval_info(visible=False)
        self.assertEqual(response.questions.first(), self.question)
