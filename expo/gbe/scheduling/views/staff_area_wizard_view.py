from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from gbe.models import UserMessage
from gbe.scheduling.forms import (
    GenericBookingForm,
    StaffAreaOccurrenceForm,
)
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from gbe.functions import validate_perms
from gbe_forms_text import event_settings


class StaffAreaWizardView(EventWizardView):
    template = 'gbe/scheduling/ticketed_event_wizard.tmpl'
    roles = ['Staff Lead', ]
    default_event_type = "general"
    event_type = "staff"

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = GenericBookingForm(
            initial={'e_conference':  self.conference,
                     'type': "Staff Area"})
        context['scheduling_form'] = StaffAreaOccurrenceForm(
            initial={'max_volunteer': event_settings[
                        self.event_type]['max_volunteer']})
        context['worker_formset'] = self.make_formset(
            event_settings[self.event_type]['roles'])
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = GenericBookingForm(request.POST)
        context['scheduling_form'] = StaffAreaOccurrenceForm(
            request.POST)
        context['worker_formset'] = self.make_formset(
            event_settings[self.event_type]['roles'],
            post=request.POST)
        if context['second_form'].is_valid(
                ) and context['scheduling_form'].is_valid(
                ) and self.is_formset_valid(context['worker_formset']):
            new_event = context['second_form'].save(commit=False)
            new_event.duration = Duration(
                minutes=context['scheduling_form'].cleaned_data[
                    'duration']*60)
            new_event.save()
            response = self.book_event(context['scheduling_form'],
                                       context['worker_formset'],
                                       new_event)
            success = self.finish_booking(
                request,
                response,
                context['scheduling_form'].cleaned_data['day'].pk)
            if success:
                if request.POST.get(
                        'set_event') == 'Continue to Volunteer Opportunities':
                    return HttpResponseRedirect(
                        reverse('edit_event',
                                urlconf='gbe.scheduling.urls',
                                args=[self.conference.conference_slug,
                                      response.occurrence.pk]))
                else:
                    return success
        return render(request, self.template, context)
