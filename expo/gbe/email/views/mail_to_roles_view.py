from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import (
    Event,
    StaffArea,
    UserMessage,
)
from gbe.email.forms import (
    SecretRoleInfoForm,
    SelectRoleForm,
)
from scheduler.idd import get_people
from gbe.email.views import MailToFilterView
from gbetext import to_list_empty_msg
from gbe_forms_text import (
    all_roles,
    role_option_privs
)
from django.forms import (
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
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

    def setup_event_queryset(self, priv_list, conferences):
        # build event field based on privs
        event_queryset = None
        if len([i for i in ["Scheduling Mavens",
                            "Registrar",
                            "Volunteer Coordinator"] if i in priv_list]) > 0:
            event_queryset = Event.objects.filter(
                e_conference__in=conferences
                ).filter(
                Q(genericevent__type__in=["Special", "Master"],) |
                Q(show__pk__gt=0))
        elif len([i for i in ['Producer',
                              'Technical Director',
                              'Act Coordinator',
                              'Staff Lead'] if i in priv_list]) > 0:
            query = None
            if 'Staff Lead' in priv_list:
                query = Q(genericevent__type__in=["Special"],)
            if len([i for i in ['Producer',
                                'Technical Director',
                                'Act Coordinator'] if i in priv_list]) > 0:
                if query:
                   query = query | Q(show__pk__gt=0)
                else:
                    query = Q(show__pk__gt=0)
            event_queryset = Event.objects.filter(
                    e_conference__in=conferences
                    ).filter(query)
        return event_queryset

    def setup_staff_queryset(self, priv_list, conferences):
        staff_queryset = None
        if len([i for i in ["Scheduling Mavens",
                            "Registrar",
                            "Volunteer Coordinator"] if i in priv_list]) > 0:
            staff_queryset = StaffArea.objects.filter(
                conference__in=self.select_form.cleaned_data['conference'])
        elif "Staff Lead" in priv_list:
            staff_queryset = StaffArea.objects.filter(
                conference__in=self.select_form.cleaned_data['conference'],
                staff_lead=self.user)
        return staff_queryset

    def setup_event_collect_choices(self, priv_list, conferences):
        event_collect_choices = []
        if len([i for i in ["Scheduling Mavens",
                            "Registrar",
                            "Volunteer Coordinator"] if i in priv_list]) > 0:
            event_collect_choices = [
                ("conf_class", "All Conference Classes"),
                ("drop-in", "All Drop-In Classes"),
                ("volunteer", "All Volunteer Events")]
        else:
            if "Class Coordinator" in priv_list:
                event_collect_choices += [
                    ("conf_class", "All Conference Classes")]
            if "Staff Lead" in priv_list:
                event_collect_choices += [
                    ("volunteer", "All Volunteer Events")]
        return event_collect_choices

    def groundwork(self, request, args, kwargs):
        self.url = reverse('mail_to_roles', urlconf='gbe.email.urls')
        priv_list = self.user.privilege_groups
        priv_list += self.user.get_roles()
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys():
            self.select_form = SelectRoleForm(
                request.POST,
                prefix="email-select")

            if self.select_form.is_valid():
                self.event_queryset = self.setup_event_queryset(
                    priv_list,
                    self.select_form.cleaned_data['conference'])
                self.staff_queryset = self.setup_staff_queryset(
                    priv_list,
                    self.select_form.cleaned_data['conference'])
                self.event_collect_choices = self.setup_event_collect_choices(
                    priv_list,
                    self.select_form.cleaned_data['conference'])

                if self.event_queryset:
                    self.select_form.fields['events'] = ModelMultipleChoiceField(
                        queryset=self.event_queryset,
                        widget=CheckboxSelectMultiple(),
                        required=True)
                if self.staff_queryset:
                    self.select_form.fields['staff_areas'] = ModelMultipleChoiceField(
                        queryset=self.staff_queryset,
                        widget=CheckboxSelectMultiple(),
                        required=True)
                if len(self.event_collect_choices) > 0:
                    self.select_form.fields[
                        'event_collections'] = MultipleChoiceField(
                        choices=self.event_collect_choices,
                        widget=CheckboxSelectMultiple(),
                        required=True)
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
        events = {}
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
        if self.event_queryset:
            recipient_info.fields['events'] = ModelMultipleChoiceField(
                queryset=self.event_queryset,
                widget=MultipleHiddenInput(),
                required=True)
        if self.staff_queryset:
            recipient_info.fields['staff_areas'] = ModelMultipleChoiceField(
                queryset=self.staff_queryset,
                required=True)
        if len(self.event_collect_choices) > 0:
            recipient_info.fields['event_collections'] = MultipleChoiceField(
                choices=self.event_collect_choices,
                widget=MultipleHiddenInput(),
                required=True)
        return render(
            request,
            self.template,
            {"selection_form": self.select_form,
             "email_forms": [email_form, recipient_info],
             "to_list": to_list, })
