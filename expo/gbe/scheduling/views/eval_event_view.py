from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Avg
from django.forms import (
    ChoiceField,
    ModelChoiceField,
)
from gbe.models import (
    Event,
    UserMessage,
)
from gbe.functions import check_user_and_redirect
from scheduler.idd import get_eval_info
from gbetext import (
    not_ready_for_eval,
    one_eval_msg,
)
from gbe.scheduling.forms import EventEvaluationForm


class EvalEventView(View):
    template = 'gbe/scheduling/eval_event.tmpl'

    def groundwork(self, request, args, kwargs):
        this_url = reverse(
                'eval_event',
                args=[kwargs['occurrence_id'], ],
                urlconf='gbe.scheduling.urls')
        response = check_user_and_redirect(
            request,
            this_url,
            self.__class__.__name__)
        if response['error_url']:
            return HttpResponseRedirect(response['error_url'])
        self.owner = response['owner']

    def setup_eval(self, request, occurrence_id):
        eval_info = get_eval_info(occurrence_id, person=self.owner)
        redirect_now = False
        if len(eval_info.errors) > 0:
            for error in eval_info.errors:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code=error.code,
                    defaults={
                        'summary': "Get Eval Warning",
                        'description': error.details})
                messages.error(request, user_message[0].description)
            redirect_now = True
        elif len(eval_info.warnings) > 0:
            for warning in eval_info.warnings:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code=warning.code,
                    defaults={
                        'summary': "Get Eval Warning",
                        'description': warning.details})
                messages.warning(request, user_message[0].description)
            redirect_now = True
        elif len(eval_info.questions) == 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NOT_READY",
                defaults={
                    'summary': "No Questions",
                    'description': not_ready_for_eval})
            messages.warning(request, user_message[0].description)
            redirect_now = True
        elif len(eval_info.answers) > 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ONLY_ONE_EVAL",
                defaults={
                    'summary': "One Eval per Attendee",
                    'description': one_eval_msg})
            messages.warning(request, user_message[0].description)
            redirect_now = True
        if request.GET.get('next', None):
            redirect_to = request.GET['next']
        else:
            redirect_to = reverse('home', urlconf='gbe.urls')
        return (redirect_to, eval_info, redirect_now)

    @never_cache
    def get(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return redirect
        redirect_to, eval_info, redirect_now = self.setup_eval(
            request,
            kwargs['occurrence_id'])
        if redirect_now:
            return HttpResponseRedirect(redirect_to)
        eval_form = EventEvaluationForm(questions=eval_info.questions)
        item = Event.objects.get(
            eventitem_id=eval_info.occurrences[0].foreign_event_id)
        context = {
            'form': eval_form,
            'occurrence': eval_info.occurrences[0],
            'event': item,
        }
        return render(request, self.template, context)

    @never_cache
    def post(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return redirect
        redirect_to, eval_info, redirect_now = self.setup_eval(
            request,
            kwargs['occurrence_id'])
        if redirect_now:
            return HttpResponseRedirect(redirect_to)
        eval_form = EventEvaluationForm(request.POST,
                                        questions=eval_info.questions)
        if eval_form.is_valid():
            raise Exception('valid')
        else:
            item = Event.objects.get(
                eventitem_id=eval_info.occurrences[0].foreign_event_id)
            context = {
                'form': eval_form,
                'occurrence': eval_info.occurrences[0],
                'event': item,
            }
            return render(request, self.template, context)

        return HttpResponseRedirect(redirect_to)
