from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import (
    Act,
    Class,
    Conference,
    Costume,
    UserMessage,
    Vendor,
    Volunteer,
)
from gbe.email.forms import (
    SecretBidderInfoForm,
    SelectBidderForm,
)
from gbe.email.views import MailView
from gbetext import (
    to_list_empty_msg,
    unknown_request,
)
from gbe.functions import (
    get_current_conference,
    validate_perms,
)
from django.db.models import Q
from django.contrib.auth.models import User


class MailToBiddersView(MailView):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]

    def groundwork(self, request, args, kwargs):
        self.bid_type_choices = []
        initial_bid_choices = []
        self.user = validate_perms(request, self.reviewer_permissions)
        priv_list = self.user.get_email_privs()
        for priv in priv_list:
            self.bid_type_choices += [(priv.title(), priv.title())]
            initial_bid_choices += [priv.title()]
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys():
            self.select_form = SelectBidderForm(
                request.POST,
                prefix="email-select")
        else:
            self.select_form = SelectBidderForm(
                prefix="email-select",
                initial={
                    'conference': Conference.objects.all().values_list(
                        'pk',
                        flat=True),
                    'bid_type': initial_bid_choices,
                    'state': [0, 1, 2, 3, 4, 5, 6], })
        self.select_form.fields['bid_type'].choices = self.bid_type_choices

    def get_to_list(self):
        query = Q()
        to_list = {}
        bid_types = self.select_form.cleaned_data['bid_type']

        query = Q(b_conference__in=self.select_form.cleaned_data['conference'])

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
            draft = False

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
        email_form = self.setup_email_form(request)
        recipient_info = SecretBidderInfoForm(request.POST,
                                              prefix="email-select")
        recipient_info.fields['bid_type'].choices = self.bid_type_choices

        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form,
             "email_forms": [email_form, recipient_info],
             "to_list": to_list, })

    def get_everyone(self, request):
        to_list = {}
        if not request.user.is_superuser:
            return to_list
        for user_object in User.objects.filter(
                is_active=True).exclude(username="limbo").order_by('email'):
            if hasattr(user_object, 'profile') and len(
                    user_object.profile.display_name) > 0:
                to_list[user_object.email] = \
                            user_object.profile.display_name
            else:
                to_list[user_object.email] = \
                            user_object.username
        return to_list

    def filter_everyone(self, request):
        to_list = self.get_everyone(request)
        if len(to_list) == 0:
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
                {"selection_form": self.select_form})
        email_form = self.setup_email_form(request)

        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form,
             "email_forms": [email_form],
             "to_list": to_list,
             "everyone": True})

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
        if 'send' in request.POST.keys():
            everyone = False
            recipient_info = None
            to_list = {}
            if 'everyone' in request.POST.keys():
                to_list = self.get_everyone(request)
                everyone = True

            elif self.select_form.is_valid():
                to_list = self.get_to_list()
                recipient_info = SecretBidderInfoForm(request.POST,
                                                      prefix="email-select")
                recipient_info.fields[
                    'bid_type'].choices = self.bid_type_choices
            if len(to_list) > 0:
                mail_form = self.send_mail(request, to_list)
                if mail_form.is_valid():
                    return HttpResponseRedirect(
                        reverse('mail_to_bidders', urlconf='gbe.email.urls'))

                else:
                    return render(
                        request,
                        'gbe/email/mail_to_bidders.tmpl',
                        {"selection_form": self.select_form,
                         "email_forms": [mail_form, recipient_info],
                         "to_list": to_list,
                         "everyone": everyone})
        elif 'everyone' in request.POST.keys():
            return self.filter_everyone(request)
        elif 'filter' in request.POST.keys() and self.select_form.is_valid():
            return self.filter_bids(request)

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
