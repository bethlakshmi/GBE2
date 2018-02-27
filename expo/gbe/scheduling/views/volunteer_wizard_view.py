from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import (
    GenericBookingForm,
    PickVolunteerTopicForm,
    ScheduleOccurrenceForm,
)
from gbe.models import Class
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from django.contrib import messages
from gbe.models import UserMessage
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
)


class VolunteerWizardView(EventWizardView):
    template = 'gbe/scheduling/volunteer_wizard.tmpl'
    roles = ['Staff Lead', ]
    default_event_type = "volunteer"

    def groundwork(self, request, args, kwargs):
        context = super(VolunteerWizardView,
                        self).groundwork(request, args, kwargs)
        context['event_type'] = "Volunteer Opportunity"
        context['second_title'] = "Choose the Volunteer Area"
        return context

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickVolunteerTopicForm(
            initial={'conference':  self.conference})
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        working_class = None
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickVolunteerTopicForm(
            request.POST,
            initial={'conference':  self.conference})
        context['third_title'] = "Make New Volunteer Opportunity"
        if 'pick_topic' in request.POST.keys() and context[
                'second_form'].is_valid():
            if context['second_form'].cleaned_data[
                    'volunteer_topic'] and 'staff_' in context[
                    'second_form'].cleaned_data['volunteer_topic']:
                staff_area_id = context['second_form'].cleaned_data[
                    'volunteer_topic'].split("staff_")[1]
                return HttpResponseRedirect(
                    "%s?start_open=False" % reverse(
                        'edit_staff',
                        urlconf='gbe.scheduling.urls',
                        args=[staff_area_id]))
            elif context['second_form'].cleaned_data[
                    'volunteer_topic']:
                occurrence_id = context['second_form'].cleaned_data[
                    'volunteer_topic']
                return HttpResponseRedirect(
                    "%s?start_open=False" % reverse(
                        'edit_event',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              occurrence_id]))
            else:
                context['third_title'] = "Make New Volunteer Opportunity"
                context['third_form'] = GenericBookingForm(
                    initial={'e_conference':  self.conference,
                             'type': "Volunteer"})
                context['scheduling_form'] = ScheduleOccurrenceForm(
                    conference=self.conference,
                    initial={'duration': 1,
                             'max_volunteer': 1})
                context['worker_formset'] = self.make_formset(self.roles)
        elif 'set_opp' in request.POST.keys():
            context['third_title'] = "Make New Volunteer Opportunity"
            context['third_form'] = GenericBookingForm(request.POST)
            context['second_form'] = PickVolunteerTopicForm(
                initial={'conference':  self.conference})
            context['scheduling_form'] = ScheduleOccurrenceForm(
                request.POST,
                conference=self.conference)
            context['worker_formset'] = self.make_formset(self.roles,
                                                          post=request.POST)
            if context['third_form'].is_valid(
                    ) and context['scheduling_form'].is_valid(
                    ) and self.is_formset_valid(context['worker_formset']):
                volunteer_event = context['third_form'].save(commit=False)
                volunteer_event.duration = Duration(
                    minutes=context['scheduling_form'].cleaned_data[
                        'duration']*60)
                volunteer_event.save()
                response = self.book_event(context['scheduling_form'],
                                           context['worker_formset'],
                                           volunteer_event)
                success = self.finish_booking(
                    request,
                    response,
                    context['scheduling_form'].cleaned_data['day'].pk)
                if success:
                    return success
        return render(request, self.template, context)
