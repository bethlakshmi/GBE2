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
from gbe.models import UserMessage
from gbe.email.forms import SelectBidderForm
from gbe.functions import validate_perms


class MailToBiddersView(View):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]

    def groundwork(self, request, args, kwargs):
        bid_type_choices = [('','All')]
        self.user = validate_perms(request, self.reviewer_permissions)
        priv_list = self.user.get_email_privs()
        self.select_form = SelectBidderForm(prefix="email-select")
        for priv in priv_list:
            bid_type_choices += [(priv, priv.title())]

        self.select_form.fields['bid_type'].choices = bid_type_choices

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form,
             "email_form": "email",
             "to_list": "to_list", }
            )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailToBiddersView, self).dispatch(*args, **kwargs)
