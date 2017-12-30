from django.db.models import CharField
from scheduler.models import EventEvalAnswer
from gbetext import yesno_options


class EventEvalYesNo(EventEvalAnswer):
    answer = CharField(choices=yesno_options,
                       blank=False,
                       max_length=10)
