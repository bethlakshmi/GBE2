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
    SecretRoleInfoForm,
    SelectRoleForm,
)
from scheduler.idd import get_people
from gbe.scheduling.views.functions import show_general_status
from gbe.email.views import MailToFilterView
from gbetext import to_list_empty_msg
from gbe_forms_text import (
    all_roles,
    role_option_privs
)
from django.db.models import Q


class MailToRolesView(MailToFilterView):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Producer',
                            'Registrar',
                            'Schedule Mavens',
                            'Staff Lead',
                            'Technical Director',
                            'Volunteer Coordinator',
                            ]
    template = 'gbe/email/mail_to_roles.tmpl'

    def groundwork(self, request, args, kwargs):
        self.url = reverse('mail_to_roles', urlconf='gbe.email.urls')
        priv_list = self.user.privilege_groups
        priv_list += self.user.get_roles()
        
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys():
            self.select_form = SelectRoleForm(
                request.POST,
                prefix="email-select")
        else:
            self.select_form = SelectRoleForm(
                prefix="email-select")

        if not (self.user.user_object.is_superuser or len(
                [i for i in all_roles if i in priv_list]) > 0):
            avail_roles = []
            for key, value in role_option_privs.iteritems():
                if key in priv_list:
                    for role in value:
                        if role not in avail_roles:
                            avail_roles.append(role)
            if len(avail_roles) == 0:
                raise Exception("no match for this role")
            self.select_form.fields['roles'].choices = [
                (role, role) for role in sorted(avail_roles)]

    def get_to_list(self):
        to_list = {}
        slugs = []
        for conference in self.select_form.cleaned_data['conference']:
            slugs += [conference.conference_slug]
        response = get_people(labels=slugs,
                              roles=self.select_form.cleaned_data['roles'])

        for person in response.people:
            to_list[person.user.email] = \
                    person.user.profile.display_name
        return to_list

    def filter_emails(self, request):
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
        recipient_info = SecretRoleInfoForm(request.POST,
                                            prefix="email-select")

        return render(
            request,
            self.template,
            {"selection_form": self.select_form,
             "email_forms": [email_form, recipient_info],
             "to_list": to_list, })
