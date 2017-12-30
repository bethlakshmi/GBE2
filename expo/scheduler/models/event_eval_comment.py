from django.db.models import (
    Model,
    ForeignKey,
    TextField,
)
from scheduler.models import (
    EventEvalQuestion,
    Event,
    WorkerItem,
)

from gbetext import grade_options


class EventEvalComment(Model):
    question = ForeignKey(EventEvalQuestion)
    comment = TextField(blank=True, max_length=500)
    profile = ForeignKey(WorkerItem)
    event = ForeignKey(Event)

    class Meta:
        app_label = "scheduler"
        unique_together = (('profile', 'event'),)
