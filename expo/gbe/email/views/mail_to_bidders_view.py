from django.views.generic import View
from django.views.decorators.cache import never_cache
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
from gbe.functions import validate_perms
from django.db.models import Q


class MailToBiddersView(View):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]

    def groundwork(self, request, args, kwargs):
        self.bid_type_choices = [('','All')]
        self.user = validate_perms(request, self.reviewer_permissions)
        priv_list = self.user.get_email_privs()
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys():
            self.select_form = SelectBidderForm(
                request.POST,
                prefix="email-select")
        else:
            self.select_form = SelectBidderForm(prefix="email-select")
        for priv in priv_list:
            self.bid_type_choices += [(priv.title(), priv.title())]

        self.select_form.fields['bid_type'].choices = self.bid_type_choices

    def filter_bids(self, request):
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

        if self.select_form.cleaned_data['state']:
            query = query & Q(
                accepted=self.select_form.cleaned_data['state'])

        for bid_type in bid_types:
            for bid in eval(bid_type).objects.filter(query):
                to_list[bid.profile.user_object.email] = bid.profile.display_name

        email_form = AdHocEmailForm(initial={'sender': self.user.user_object.email})
        recipient_info = SecretBidderInfoForm(initial={
            'conference': self.select_form.cleaned_data['conference'],
            'bid_type': self.select_form.cleaned_data['bid_type'],
            'state': self.select_form.cleaned_data['state'],
            'to_list': to_list,
            },prefix="email-select")
        recipient_info.fields['bid_type'].choices = self.bid_type_choices
        recipient_info.fields['to_list'].initial = to_list

        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form,
             "email_forms": [email_form, recipient_info],
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
        elif 'send' in request.POST.keys():
            mail_form = AdHocEmailForm(request.POST)
            recipient_info = SecretBidderInfoForm(request.POST,
                                                  prefix="email-select")
            recipient_info.fields['bid_type'].choices = self.bid_type_choices
            if mail_form.is_valid():
                pass
            else:
                return render(
                    request,
                    'gbe/email/mail_to_bidders.tmpl',
                     {"selection_form": self.select_form,
                      "email_forms": [mail_form, recipient_info],
                      "to_list": eval(request.POST["email-select-to_list"]), })
        else:
            return render(
                request,
                'gbe/email/mail_to_bidders.tmpl',
                {"selection_form": self.select_form, }
                 )
        

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailToBiddersView, self).dispatch(*args, **kwargs)
