from django.db.models import (
    Model,
    ForeignKey,
    CharField,
)
from scheduler.models import (
    EventEvalQuestion,
    Event,
    WorkerItem,
)

from gbetext import grade_options


class EventEvalGrade(Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    question = ForeignKey(EventEvalQuestion)
    rating = CharField(choices=grade_options,
                       blank=True,
                       max_length=10)
    profile = ForeignKey(WorkerItem)
    event = ForeignKey(Event)

    class Meta:
        app_label = "scheduler"
        unique_together = (('question', 'profile', 'event'),)
