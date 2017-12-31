from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.shortcuts import render
from gbe.models import (
    Event,
    Performer,
    UserMessage,
)
from gbe.functions import check_user_and_redirect
from scheduler.idd import (
    get_bookings,
    get_eval_info,
    set_eval_info,
)
from scheduler.data_transfer import (
    Answer,
    Person,
)
from gbetext import (
    eval_intro_msg,
    eval_success_msg,
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
        self.person = Person(
            user=response['owner'].user_object,
            public_id=response['owner'].pk,
            public_class="Profile")

    def setup_eval(self, request, occurrence_id):
        eval_info = get_eval_info(occurrence_id, person=self.person)
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

    def make_context(self, eval_form, eval_info):
        item = Event.objects.get(
            eventitem_id=eval_info.occurrences[0].foreign_event_id)
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
                    code="EVALUATION_INTRO",
                    defaults={
                        'summary': "Evaluation Introduction",
                        'description': eval_intro_msg})
        response = get_bookings(occurrence_ids=[eval_info.occurrences[0].pk],
                                  roles=['Teacher', 'Moderator', 'Panelist'])
        presenters = []
        for person in response.people:
            presenters += [{
                'presenter': eval(person.public_class).objects.get(
                    pk=person.public_id),
                'role': person.role,
            }]
        context = {
            'form': eval_form,
            'occurrence': eval_info.occurrences[0],
            'event': item,
            'intro': user_message[0].description,
            'presenters': presenters,
        }
        return context

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
        return render(request,
                      self.template,
                      self.make_context(eval_form, eval_info))

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
            answers = []
            for question in eval_info.questions:
                answers += [
                    Answer(
                        question=question,
                        value=eval_form.cleaned_data[
                            'question%d' % question.id],
                    )
                ]
            eval_response = set_eval_info(answers,
                                          kwargs['occurrence_id'],
                                          self.person)
            if len(eval_response.answers) > 0 and len(
                    eval_response.occurrences) > 0:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="EVALUATION_SAVED",
                    defaults={
                        'summary': "Evaluation Submitted",
                        'description': eval_success_msg})
                messages.info(request, user_message[0].description)
            elif len(eval_response.warnings) > 0:
                for warning in eval_response.warnings:
                    user_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code=warning.code,
                        defaults={
                            'summary': "Get Eval Warning",
                            'description': warning.details})
                    messages.warning(request, user_message[0].description)
        else:
            return render(request,
                          self.template,
                          self.make_context(eval_form, eval_info))

        return HttpResponseRedirect(redirect_to)
