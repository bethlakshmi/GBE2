from django.db.models import CharField
from scheduler.models import EventEvalAnswer
from gbetext import grade_options


class EventEvalGrade(EventEvalAnswer):
    answer = CharField(choices=grade_options,
                       blank=True,
                       max_length=10)
