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
from django.db.models import Count, Avg


def get_eval_summary(labels, visible=True):
    summaries = {}
    response = get_occurrences(labels=labels)
    if len(response.errors) > 0:
        return EvalSummaryResponse(errors=response.errors)

    questions = EventEvalQuestion.objects.filter(
        visible=visible).exclude(answer_type="text").order_by(
        'order')

    for question in questions:
        summary = None
        if question.answer_type == "boolean":
            summary = EventEvalBoolean.objects.filter(
                event__in=response.occurrences,
                question=question).values(
                'event').annotate(
                summary=Avg('answer'))
        if question.answer_type == "grade":
            summary = EventEvalGrade.objects.filter(
                event__in=response.occurrences,
                question=question).values(
                'event', 'answer').annotate(
                summary=Count('answer'))
        summaries[question.pk] = summary

    question = EventEvalQuestion.objects.filter(
        visible=visible,
        answer_type="grade").first()
    count = EventEvalGrade.objects.filter(
        question=question).values('event').annotate(
        eval_count=Count('event'))
    return EvalSummaryResponse(occurrences=response.occurrences,
                               questions=questions,
                               summaries=summaries,
                               count=count)
