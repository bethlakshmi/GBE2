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
from gbe.email.views import MailToFilterView
from gbetext import (
    to_list_empty_msg,
)
from django.db.models import Q


class MailToRolesView(MailToFilterView):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Producer',
                            'Registrar',
                            'Schedule Mavens',
                            'Staff Lead',
                            'Technical Director',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]
    template = 'gbe/email/mail_to_roles.tmpl'

    def groundwork(self, request, args, kwargs):
        self.url = reverse('mail_to_roles', urlconf='gbe.email.urls')
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys():
            self.select_form = SelectRoleForm(
                request.POST,
                prefix="email-select")
        else:
            self.select_form = SelectRoleForm(
                prefix="email-select")

    def get_to_list(self):
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
                self.template,
                {"selection_form": self.select_form})
        email_form = self.setup_email_form(request)
        recipient_info = SecretBidderInfoForm(request.POST,
                                              prefix="email-select")
        recipient_info.fields['bid_type'].choices = self.bid_type_choices

        return render(
            request,
            self.template,
            {"selection_form": self.select_form,
             "email_forms": [email_form, recipient_info],
             "to_list": to_list, })
