from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import (
    GenericBookingForm,
    PickClassForm,
    ScheduleOccurrenceForm,
)
from gbe.scheduling.views import EventWizardView
from gbe.scheduling.views.functions import (
    show_scheduling_occurrence_status,
)
from gbe.duration import Duration
from django.contrib import messages
from gbe.models import UserMessage
from ticketing.forms import LinkBPTEventForm
from gbe.functions import validate_perms


class TicketedClassWizardView(EventWizardView):
    template = 'gbe/scheduling/ticketed_class_wizard.tmpl'
    roles = ['Teacher', 'Volunteer', 'Staff Lead']
    default_event_type = "general"

    def groundwork(self, request, args, kwargs):
        context = super(TicketedClassWizardView,
                        self).groundwork(request, args, kwargs)
        self.event_type = kwargs['event_type']
        context['event_type'] = "%s Class" % self.event_type.title()
        context['second_title'] = "Make New Class"
        context['tickets'] = None
        return context

    def make_formset(self, post=None):
        if self.event_type == 'master':
            formset = super(TicketedClassWizardView, self).make_formset(
                ['Teacher', 'Volunteer',], post=post)
        else:
            formset = super(TicketedClassWizardView, self).make_formset(
                ['Staff Lead', 'Teacher', 'Volunteer',], post=post)
        return formset

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = GenericBookingForm(
            initial={'e_conference':  self.conference,
                     'type': self.event_type.title()})
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=self.conference,
            open_to_public=True,
            initial={'duration': 1, })
        context['worker_formset'] = self.make_formset()
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkBPTEventForm(initial={
                'conference': self.conference,})
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = GenericBookingForm(request.POST)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            request.POST,
            conference=self.conference)
        context['worker_formset'] = self.make_formset(post=request.POST)
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkBPTEventForm(request.POST, initial={
                'conference': self.conference,})
        if context['second_form'].is_valid(
                ) and context['scheduling_form'].is_valid(
                ) and self.is_formset_valid(context['worker_formset']) and (
                not context['tickets'] or context['tickets'].is_valid()):
            working_class = context['second_form'].save(commit=False)
            working_class.duration = Duration(
                minutes=context['scheduling_form'].cleaned_data[
                    'duration']*60)
            working_class.save()
            response = self.book_event(context['scheduling_form'],
                                       context['worker_formset'],
                                       working_class)
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)
            if response.occurrence:
                return HttpResponseRedirect(
                    "%s?%s-day=%d&filter=Filter&new=%s" % (
                        reverse('manage_event_list',
                                urlconf='gbe.scheduling.urls',
                                args=[self.conference.conference_slug]),
                        self.conference.conference_slug,
                        context['scheduling_form'].cleaned_data['day'].pk,
                        str([response.occurrence.pk]),))
        return render(request, self.template, context)
