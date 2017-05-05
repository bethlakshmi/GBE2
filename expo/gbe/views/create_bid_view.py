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


class CreateBidView(View):
    form = None
    fee_link = None
    popup_text = None

    def groundwork(self, request, args, kwargs):
        self.owner = validate_profile(request, require=True)
        self.conference = Conference.objects.filter(
            accepting_bids=True).first()

    def set_up_post(self, request):
        if 'submit' in request.POST.keys():
            self.form = self.submit_form(request.POST, prefix=self.prefix)
            return UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "%s Submit Success" % self.bid_type,
                    'description': self.submit_msg})
        else:
            self.form = self.draft_form(request.POST, prefix=self.prefix)
            return UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "%s Draft Success" % self.bid_type,
                    'description': self.draft_msg})

    def make_context(self):
        context = {
            'forms': [self.form],
            'page_title': self.page_title,
            'view_title': self.view_title,
            'draft_fields': self.draft_fields,
            'submit_fields': self.submit_fields}
        return context

    def get_create_form(self, request):
        self.set_up_form()

        return render(
            request,
            'gbe/bid.tmpl',
            self.make_context()
        )

    @never_cache
    @log_func
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return (self.user_not_ready_redirect() or
                self.get_create_form(request))

    @never_cache
    @log_func
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        user_message = self.set_up_post(request)
        if self.form.is_valid():
            self.bid_object = self.form.save(commit=False)
            self.set_valid_form(request)

            if 'submit' in request.POST.keys():
                if self.fee_paid():
                    if self.bid_object.complete:
                        self.bid_object.submitted = True
                        self.bid_object.save()
                    else:
                        context = self.make_context()
                        context['errors'] = [
                            'Cannot submit, %s is not complete' % (
                                self.bid_type.lower())]
                        return render(
                            request,
                           'gbe/bid.tmpl',
                           context
                        )
                else:
                    page_title = '%s Payment' % self.bid_type
                    return render(
                        request,
                        'gbe/please_pay.tmpl',
                        {'link': self.fee_link,
                         'page_title': page_title})
            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            return self.get_invalid_response(request)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateBidView, self).dispatch(*args, **kwargs)

