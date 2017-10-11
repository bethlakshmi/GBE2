from django.views.generic import View
from django.forms import HiddenInput
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from gbe.models import UserMessage
from gbe.email.forms import AdHocEmailForm
from gbetext import send_email_success_msg
from post_office import mail


class MailView(View):

    def setup_email_form(self, request):
        email_form = AdHocEmailForm(initial={
            'sender': self.user.user_object.email})
        if not request.user.is_superuser:
            email_form.fields['sender'].widget = HiddenInput()
        return email_form

    def send_mail(self, request, to_list):
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

            for email, name in to_list.iteritems():
                email_batch += [{
                    'sender': sender,
                    'recipients': [email],
                    'subject': mail_form.cleaned_data['subject'],
                    'html_message': mail_form.cleaned_data['html_message'], }]
                recipient_string = "%s (%s), %s" % (
                    name,
                    email,
                    recipient_string)

            mail.send_many(email_batch)
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SEND_SUCCESS",
                defaults={
                    'summary': "Email Sent to Bidders",
                    'description': send_email_success_msg})
            messages.success(
                request,
                user_message[0].description + recipient_string)
        return mail_form

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailView, self).dispatch(*args, **kwargs)
