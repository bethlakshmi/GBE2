from scheduler.models import (
    EventEvalComment,
    EventEvalGrade,
    EventEvalBoolean,
    EventEvalQuestion,
)
from scheduler.data_transfer import (
    EvalSummaryResponse,
)
from scheduler.idd import get_occurrences
from datetime import (
    datetime,
    timedelta,
)
import pytz
from django.conf import settings


def get_eval_summary(labels, visible=True):
    summaries = {}
    response = get_occurrences(labels=labels)
    if len(response.errors) > 0:
        return EvalSummaryResponse(errors=response.errors)

    questions = EventEvalQuestion.objects.filter(
        visible=visible).order_by(
        'order')

    
    return EvalSummaryResponse(occurrences=response.occurrences,
                               questions=questions,
                               summaries=summaries)
