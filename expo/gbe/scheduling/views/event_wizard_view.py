from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from gbe.functions import validate_perms
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import (
    PersonAllocationForm,
    PickEventForm,
)
from gbe.models import Conference


class EventWizardView(View):
    template = 'gbe/scheduling/event_wizard.tmpl'
    permissions = ('Scheduling Mavens',)
    default_event_type = None

    role_map = {
        'Staff Lead': False,
        'Moderator': True,
        'Teacher': True,
        'Panelist': True,
        'Volunteer': False,
    }

    def get_pick_event_form(self, request):
        if 'pick_event' in request.GET.keys():
            return PickEventForm(request.GET)
        elif self.default_event_type:
            return PickEventForm(initial={
                'event_type': self.default_event_type})
        else:
            return PickEventForm()

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        if "conference" in kwargs:
            self.conference = get_object_or_404(
                Conference,
                conference_slug=kwargs['conference'])
        context = {
            'selection_form':  self.get_pick_event_form(request),
            'conference_slug': self.conference.conference_slug,
        }
        return context

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        if 'pick_event' in request.GET.keys() and context[
                'selection_form'].is_valid():
            if context['selection_form'].cleaned_data[
                    'event_type'] == 'conference':
                return HttpResponseRedirect("%s?%s" % (
                    reverse('create_class_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    request.GET.urlencode()))
            if context['selection_form'].cleaned_data[
                    'event_type'] in ('drop-in', 'master'):
                return HttpResponseRedirect("%s?%s" % (
                    reverse('create_ticketed_class_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug,
                                  context['selection_form'].cleaned_data[
                                    'event_type']]),
                    request.GET.urlencode()))
        return render(request, self.template, context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventWizardView, self).dispatch(*args, **kwargs)

    def make_formset(self, roles, initial=None, post=None):
        formset = []
        n = 0
        for role in roles:
            if n == 0 and initial:
                formset += [PersonAllocationForm(
                    post,
                    label_visible=False,
                    role_options=[(initial['role'], initial['role']),],
                    use_personas=self.role_map[initial['role']],
                    initial=initial,
                    prefix="role_0")]
            formset += [PersonAllocationForm(
                post,
                label_visible=False,
                role_options=[(role, role),],
                use_personas=self.role_map[role],
                initial={'role': role},
                prefix="role_%d" % n),]
            n = n + 1
        return formset

    def is_formset_valid(self, formset):
        validity = False
        for form in formset:
            validity = form.is_valid() or validity
        return validity