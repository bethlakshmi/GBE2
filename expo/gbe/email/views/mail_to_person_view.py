from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.forms import HiddenInput
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import (
    Profile,
    UserMessage
)
from gbe.email.forms import AdHocEmailForm
from gbetext import (
    send_email_success_msg,
    to_list_empty_msg,
    unknown_request,
)
from gbe.functions import validate_perms
from post_office import mail


class MailToPersonView(View):
    email_permissions = ['Act Coordinator',
                         'Class Coordinator',
                         'Costume Coordinator',
                         'Vendor Coordinator',
                         'Volunteer Coordinator',
                         ]

    def groundwork(self, request, args, kwargs):
        self.user = validate_perms(request, self.email_permissions)
        if "profile_id" in kwargs:
            profile_id = kwargs.get('profile_id')
            user_profile = Profile.objects.get(resourceitem_id=profile_id)
        else:
            raise Exception('no id')
        return user_profile.user_object.email

    def send_mail(self, request, to_address):
        mail_form = AdHocEmailForm(request.POST)
        if not request.user.is_superuser:
            mail_form.fields['sender'].widget = HiddenInput()
        if mail_form.is_valid():
            email_batch = []
            recipient_string = ""
            if request.user.is_superuser:
                sender = mail_form.cleaned_data['sender']
            else:
                sender = request.user.email

            mail.send(
                [to_address],
                sender,
                subject=mail_form.cleaned_data['subject'],
                html_message=mail_form.cleaned_data['html_message'])

            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SEND_SUCCESS",
                defaults={
                    'summary': "Email Sent to Person",
                    'description': send_email_success_msg})
            messages.success(
                request,
                user_message[0].description + to_address)
            return HttpResponseRedirect(
                reverse('home', urlconf='gbe.urls'))

        else:
            return render(
                request,
                'gbe/email/send_mail.tmpl',
                {"to_address": to_address,
                 "email_form": mail_form})

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        to_address = self.groundwork(request, args, kwargs)
        email_form = AdHocEmailForm(initial={
            'sender': self.user.user_object.email})
        if not request.user.is_superuser:
            email_form.fields['sender'].widget = HiddenInput()
        return render(
            request,
            'gbe/email/send_mail.tmpl',
            {"to_address": to_address,
             "email_form": email_form}
             )

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        to_address = self.groundwork(request, args, kwargs)
        return self.send_mail(request, to_address)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailToPersonView, self).dispatch(*args, **kwargs)
