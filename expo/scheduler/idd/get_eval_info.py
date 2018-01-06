from scheduler.models import (
    EventEvalComment,
    EventEvalGrade,
    EventEvalBoolean,
    EventEvalQuestion,
)
from scheduler.data_transfer import (
    EvalInfoResponse,
    Warning,
)
from scheduler.idd import get_occurrence
from datetime import (
    datetime,
    timedelta,
)
import pytz


def get_eval_info(occurrence_id=None, person=None, visible=True):
    occurrences = []
    if occurrence_id:
        response = get_occurrence(occurrence_id)
        if len(response.errors) > 0:
            return EvalInfoResponse(errors=response.errors)
        occurrences += [response.occurrence]
        if response.occurrence.starttime > (datetime.now(
                tz=pytz.timezone('America/New_York')) - timedelta(hours=4)):
            return EvalInfoResponse(
                warnings=[Warning(
                    code="EVENT_IN_FUTURE",
                    details="The event hasn't occurred yet, " +
                            "and can't be rated.",
                    occurrence=response.occurrence)],
                occurrences=occurrences)
    questions = EventEvalQuestion.objects.filter(visible=visible)
    answers = []
    for eval_type in [EventEvalComment, EventEvalGrade, EventEvalBoolean]:
        some_answers = eval_type.objects.all()
        if occurrence_id:
            some_answers = some_answers.filter(event__in=occurrences)
        if person:
            some_answers = some_answers.filter(profile__pk=person.public_id)
        answers += list(some_answers)
    if len(occurrences) == 0:
        for answer in answers:
            if answer.event not in occurrences:
                occurrences += [answer.event]
    return EvalInfoResponse(occurrences=occurrences,
                            questions=questions,
                            answers=answers)
