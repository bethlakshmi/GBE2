from scheduler.models import (
    EventEvalAnswer,
    EventEvalQuestion,
)
from scheduler.data_transfer import (
    EvalInfoResponse,
    Warning,
)
from scheduler.idd import get_occurrence
from datetime import datetime
import pytz


def get_eval_info(occurrence_id=None, person=None, visible=True):
    occurrences = []
    warnings = []
    if occurrence_id:
        response = get_occurrence(occurrence_id)
        if len(response.errors) > 0:
            return EvalInfoResponse(errors=response.errors)
        occurrences += [response.occurrence]
        if response.occurrence.starttime > datetime.now(tz=pytz.timezone('America/New_York')):
            return EvalInfoResponse(
                warnings=[Warning(
                    code="EVENT_IN_FUTURE",
                    details="The event hasn't occurred yet, and can't be rated.",
                    occurrence=response.occurrence)],
                occurrences=occurrences)
    questions = EventEvalQuestion.objects.filter(visible=visible)
    answers = EventEvalAnswer.objects.filter(event__in=occurrences)
    if person:
        answers = answers.filters(profile=person)
    return EvalInfoResponse(occurrences=occurrences,
                            questions=questions,
                            answers=answers)
