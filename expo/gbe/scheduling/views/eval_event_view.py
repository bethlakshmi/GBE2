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
    UserMessage,
)
from gbe.functions import check_user_and_redirect
from scheduler.idd import get_eval_info


class EvalEventView(View):
    review_template = 'gbe/eval_class.tmpl'

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
        if len(eval_info.errors) > 0:
            for error in eval_info.errors:
                user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code=error.code,
                defaults={
                    'summary': "Get Eval Warning",
                    'description': error.details})
                messages.error(request, user_message[0].description)
        if len(eval_info.warnings) > 0:
            for warning in eval_info.warnings:
                user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code=warning.code,
                defaults={
                    'summary': "Get Eval Warning",
                    'description': warning.details})
                messages.warning(request, user_message[0].description)
        if request.GET.get('next', None):
            redirect_to = request.GET['next']
        else:
            redirect_to = reverse('home', urlconf='gbe.urls')
        return (redirect_to, eval_info)

    @never_cache
    def get(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        redirect_to, eval_info = self.setup_eval(request,
                                                 kwargs['occurrence_id'])
        if len(eval_info.errors) > 0 or len(eval_info.warnings) > 0:
            return HttpResponseRedirect(redirect_to)
        return HttpResponseRedirect(redirect_to)

    @never_cache
    def post(self, request, *args, **kwargs):
        redirect = self.groundwork(request, args, kwargs)
        redirect_to, eval_info = self.setup_eval(request,
                                                 kwargs['occurrence_id'])
        if len(eval_info.errors) > 0 or len(eval_info.warnings) > 0:
            return HttpResponseRedirect(redirect_to)
        return HttpResponseRedirect(redirect_to)
