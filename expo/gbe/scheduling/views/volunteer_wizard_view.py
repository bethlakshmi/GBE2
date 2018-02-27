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
    ClassBookingForm,
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

    def get_scheduling_info(self, bid_class):
        schedule_opt = dict(class_schedule_options)
        scheduling_info = {
            'display_info': [
                (classbid_labels['schedule_constraints'],
                 ', '.join([j for i, j in class_schedule_options
                            if i in bid_class.schedule_constraints])),
                (classbid_labels['avoided_constraints'],
                 ', '.join(
                    [j for i, j in class_schedule_options
                     if i in bid_class.avoided_constraints])),
                ('Space Needs', bid_class.get_space_needs_display()), ],
            'reference': reverse('class_view',
                                 urlconf='gbe.urls',
                                 args=[bid_class.id]),
            }
        return scheduling_info

    def make_formset(self, working_class=None, post=None):
        if working_class:
            if working_class.type == 'Panel':
                formset = super(VolunteerWizardView, self).make_formset(
                    ['Moderator',
                     'Panelist',
                     'Panelist',
                     'Panelist',
                     'Panelist'],
                    initial={
                        'role': 'Moderator',
                        'worker': working_class.teacher},
                    post=post)
            else:
                formset = super(VolunteerWizardView, self).make_formset(
                    ['Teacher',
                     'Teacher',
                     'Teacher'],
                    initial={
                        'role': 'Teacher',
                        'worker': working_class.teacher},
                    post=post)
        else:
                formset = super(VolunteerWizardView, self).make_formset(
                    ['Teacher',
                     'Moderator',
                     'Panelist',
                     'Panelist',
                     'Panelist'],
                    post=post)
        return formset

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
            else:
                occurrence_id = context['second_form'].cleaned_data[
                    'volunteer_topic']
                return HttpResponseRedirect(
                    "%s?start_open=False" % reverse(
                        'edit_event',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              occurrence_id]))

        elif 'set_class' in request.POST.keys(
                ) and 'eventitem_id' in request.POST.keys():
            if request.POST['eventitem_id']:
                working_class = get_object_or_404(
                    Class,
                    eventitem_id=request.POST['eventitem_id'])
                context['third_title'] = "Book Class:  %s" % (
                    working_class.e_title)
                context['third_form'] = ClassBookingForm(
                    request.POST,
                    instance=working_class)
                context['scheduling_info'] = self.get_scheduling_info(
                    working_class)
            else:
                context['third_form'] = ClassBookingForm(request.POST)
            context['second_form'] = PickClassForm(
                initial={'conference':  self.conference,
                         'accepted_class': working_class})
            context['scheduling_form'] = ScheduleOccurrenceForm(
                request.POST,
                conference=self.conference)
            context['scheduling_form'].fields[
                'max_volunteer'].widget = HiddenInput()
            context['worker_formset'] = self.make_formset(working_class,
                                                          post=request.POST)
            if context['third_form'].is_valid(
                    ) and context['scheduling_form'].is_valid(
                    ) and self.is_formset_valid(context['worker_formset']):
                working_class = context['third_form'].save(commit=False)
                working_class.duration = Duration(
                    minutes=context['scheduling_form'].cleaned_data[
                        'duration']*60)
                if not hasattr(working_class, 'teacher'):
                    teacher = None
                    for form in context['worker_formset']:
                        if form.cleaned_data['worker']:
                            teacher = form.cleaned_data['worker']
                            break
                    if teacher:
                        working_class.teacher = teacher
                    else:
                        user_message = UserMessage.objects.get_or_create(
                            view=self.__class__.__name__,
                            code="NEED_LEADER",
                            defaults={
                                'summary': "Need Leader for Class",
                                'description': "You must select at least " +
                                "one person to run this class."})
                        messages.error(
                            request,
                            user_message[0].description)
                        return render(request, self.template, context)
                    working_class.e_conference = self.conference
                    working_class.b_conference = self.conference

                working_class.save()
                response = self.book_event(context['scheduling_form'],
                                           context['worker_formset'],
                                           working_class)
                success = self.finish_booking(
                    request,
                    response,
                    context['scheduling_form'].cleaned_data['day'].pk)
                if success:
                    return success
        return render(request, self.template, context)
