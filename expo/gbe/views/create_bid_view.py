from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from gbe.models import (
    Conference,
    UserMessage
)
from expo.gbe_logging import log_func
from gbe.functions import validate_profile
from gbe_forms_text import avoided_constraints_popup_text


class CreateBidView(View):

    def groundwork(self, request, args, kwargs):
        self.owner = validate_profile(request, require=True)

    def set_up_post(self, request):
        if 'submit' in request.POST.keys():
            self.form = self.submit_form(request.POST)
            return UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "%s Submit Success" % self.bid_type,
                    'description': self.submit_msg})
        else:
            self.form = self.draft_form(request.POST)
            return UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "%s Draft Success" % self.bid_type,
                    'description': self.draft_msg})

    def get_create_form(self, request):
        self.set_up_form()

        return render(
            request,
            'gbe/bid.tmpl',
            {'forms': [self.form],
             'page_title': self.page_title,
             'view_title': self.view_title,
             'draft_fields': self.draft_fields,
             'submit_fields': self.submit_fields,
             'popup_text': avoided_constraints_popup_text}
        )

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return (self.user_not_ready_redirect() or
                self.get_create_form(request))

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        user_message = self.set_up_post(request)
        if self.form.is_valid():
            conference = Conference.objects.filter(accepting_bids=True).first()
            self.bid_object = self.form.save(commit=False)
            self.bid_object.b_conference = conference
            self.set_bid_form()
            self.bid_object = self.form.save(commit=True)

            if 'submit' in request.POST.keys():
                if self.bid_object.complete:
                    self.bid_object.submitted = True
                    self.bid_object.save()
                else:
                    error_string = 'Cannot submit, %s is not complete' % (
                        self.bid_type.lower())
                    return render(
                        request,
                        'gbe/bid.tmpl',
                        {'forms': [self.form],
                         'page_title': self.page_title,
                         'view_title': self.view_title,
                         'draft_fields': self.draft_fields,
                         'errors': [error_string],
                         'popup_text': avoided_constraints_popup_text})

            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            return self.get_create_form(request)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateBidView, self).dispatch(*args, **kwargs)

