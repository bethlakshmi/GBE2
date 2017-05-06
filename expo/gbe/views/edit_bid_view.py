from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.models import (
    UserMessage
)
from expo.gbe_logging import log_func
from gbe.functions import validate_profile


class EditBidView(View):
    form = None
    fee_link = None
    popup_text = None

    def groundwork(self, request, args, kwargs):
        bid_id = kwargs.get("bid_id")
        self.owner = validate_profile(request, require=False)
        self.bid_object = get_object_or_404(self.bid_class, pk=bid_id)

    def set_up_post(self, request):
        if 'submit' in request.POST.keys():
            self.form = self.submit_form(
                request.POST,
                instance=self.bid_object,
                initial=self.get_initial(),
                prefix=self.prefix)
            return UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "%s Edit & Submit Success" % self.bid_type,
                    'description': self.submit_msg})
        else:
            self.form = self.draft_form(
                request.POST,
                instance=self.bid_object,
                initial=self.get_initial(),
                prefix=self.prefix)
            return UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "%s Edit Draft Success" % self.bid_type,
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
        
        if not self.owner:
            return HttpResponseRedirect(
                reverse('profile_update', urlconf='gbe.urls'))

        return self.get_create_form(request)

    @never_cache
    @log_func
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if not self.owner:
            return HttpResponseRedirect(
                reverse('profile_update', urlconf='gbe.urls'))

        user_message = self.set_up_post(request)
        if not self.check_validity(request):
            return self.get_invalid_response(request)

        self.bid_object = self.form.save(commit=False)
        self.set_valid_form(request)

        if 'submit' in request.POST.keys():
            if not self.fee_paid():
                page_title = '%s Payment' % self.bid_type
                return render(
                    request,
                    'gbe/please_pay.tmpl',
                    {'link': self.fee_link,
                     'page_title': page_title})
            else:
                self.bid_object.submitted = True
                self.bid_object.save()
        messages.success(request, user_message[0].description)
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditBidView, self).dispatch(*args, **kwargs)
