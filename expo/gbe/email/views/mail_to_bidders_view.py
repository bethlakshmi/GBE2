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
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import (
    Act,
    Class,
    Costume,
    UserMessage,
    Vendor,
    Volunteer,
)
from gbe.email.forms import (
    AdHocEmailForm,
    SecretBidderInfoForm,
    SelectBidderForm,
)
from gbetext import (
    send_email_success_msg,
    to_list_empty_msg,
    unknown_request,
)
from gbe.functions import validate_perms
from django.db.models import Q
from post_office import mail


class MailToBiddersView(View):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]

    def groundwork(self, request, args, kwargs):
        self.bid_type_choices = [('', 'All')]
        self.user = validate_perms(request, self.reviewer_permissions)
        priv_list = self.user.get_email_privs()
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys():
            self.select_form = SelectBidderForm(
                request.POST,
                prefix="email-select")
        else:
            self.select_form = SelectBidderForm(prefix="email-select",
                                                initial={'state': [0, 1, 2, 3, 4, 5, 6]})
        for priv in priv_list:
            self.bid_type_choices += [(priv.title(), priv.title())]

        self.select_form.fields['bid_type'].choices = self.bid_type_choices

    def get_to_list(self):
        query = Q()
        to_list = {}
        if self.select_form.cleaned_data['bid_type']:
            bid_types = [self.select_form.cleaned_data['bid_type'], ]
        else:
            bid_types = []
            for priv in self.user.get_email_privs():
                bid_types += [priv.title(), ]

        if self.select_form.cleaned_data['conference']:
            query = query & Q(
                b_conference=self.select_form.cleaned_data['conference'])

        accept_states = self.select_form.cleaned_data['state']
        draft = False
        if "Draft" in self.select_form.cleaned_data['state']:
            draft = True
            accept_states.remove('Draft')
            draft_query = query & Q(submitted=False)

        if len(accept_states) > 0:
            query = query & Q(accepted__in=accept_states) & Q(submitted=True)
        elif draft:
            query = draft_query
            draft=False

        for bid_type in bid_types:
            for bid in eval(bid_type).objects.filter(query):
                if bid.profile.user_object.is_active:
                    to_list[bid.profile.user_object.email] = \
                        bid.profile.display_name
            if draft:
                for bid in eval(bid_type).objects.filter(draft_query):
                    if bid.profile.user_object.is_active:
                        to_list[bid.profile.user_object.email] = \
                            bid.profile.display_name
        return to_list

    def filter_bids(self, request):
        to_list = self.get_to_list()
        if len(to_list) == 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_RECIPIENTS",
                defaults={
                    'summary': "Email Sent to Bidders",
                    'description': to_list_empty_msg})
            messages.error(
                request,
                user_message[0].description)
            return render(
                request,
                'gbe/email/mail_to_bidders.tmpl',
                {"selection_form": self.select_form})
        email_form = AdHocEmailForm(initial={
            'sender': self.user.user_object.email})
        if not request.user.is_superuser:
            email_form.fields['sender'].widget = HiddenInput()
        recipient_info = SecretBidderInfoForm(initial={
            'conference': self.select_form.cleaned_data['conference'],
            'bid_type': self.select_form.cleaned_data['bid_type'],
            'state': self.select_form.cleaned_data['state'],
            }, prefix="email-select")
        recipient_info.fields['bid_type'].choices = self.bid_type_choices

        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form,
             "email_forms": [email_form, recipient_info],
             "to_list": to_list, })

    def send_mail(self, request, to_list):
        mail_form = AdHocEmailForm(request.POST)
        if not request.user.is_superuser:
            mail_form.fields['sender'].widget = HiddenInput()
        recipient_info = SecretBidderInfoForm(request.POST,
                                              prefix="email-select")
        recipient_info.fields['bid_type'].choices = self.bid_type_choices
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
            return HttpResponseRedirect(
                reverse('mail_to_bidders', urlconf='gbe.email.urls'))

        else:
            return render(
                request,
                'gbe/email/mail_to_bidders.tmpl',
                {"selection_form": self.select_form,
                 "email_forms": [mail_form, recipient_info],
                 "to_list": to_list, })

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form, }
             )

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        if 'filter' in request.POST.keys() and self.select_form.is_valid():
            return self.filter_bids(request)
        elif 'send' in request.POST.keys() and self.select_form.is_valid():
            to_list = self.get_to_list()
            return self.send_mail(request, to_list)
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="UNKNOWN_ACTION",
            defaults={
                'summary': "Unknown Request",
                'description': unknown_request})
        messages.error(
                request,
                user_message[0].description)
        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form, }
            )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailToBiddersView, self).dispatch(*args, **kwargs)
