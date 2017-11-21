from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import (
    ClassBookingForm,
    GenericBookingForm,
    PickClassForm,
    ScheduleOccurrenceForm,
)
from gbe.models import (
    Class,
    Room,
)
from gbe.functions import validate_perms
from gbe.scheduling.views import EventWizardView
from functools import partial, wraps
from gbe.scheduling.views.functions import (
    get_start_time,
    show_scheduling_occurrence_status,
)
from scheduler.data_transfer import Person
from scheduler.idd import create_occurrence
from gbe.duration import Duration
from django.contrib import messages
from gbe.models import UserMessage
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
)


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
        return context

    def book_event(self, scheduling_form, people_formset, working_class):
        room = get_object_or_404(
            Room,
            name=scheduling_form.cleaned_data['location'])
        max_volunteer = 0
        start_time = get_start_time(scheduling_form.cleaned_data)
        labels = [self.conference.conference_slug]
        if working_class.calendar_type:
                labels += [working_class.calendar_type]
        people = []
        for assignment in people_formset:
            if assignment.cleaned_data[
                    'role'
                    ] in self.roles and assignment.cleaned_data['worker']:
                people += [Person(
                    user=assignment.cleaned_data[
                        'worker'].workeritem.as_subtype.user_object,
                    public_id=assignment.cleaned_data['worker'].workeritem.pk,
                    role=assignment.cleaned_data['role'])]
        response = create_occurrence(
                working_class.eventitem_id,
                start_time,
                0,
                people=people,
                locations=[room],
                labels=labels)
        return response


    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = GenericBookingForm(
            initial={'e_conference':  self.conference,
                     'type': self.event_type})
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=self.conference,
            open_to_public=True,
            initial={'duration': 1, })
        if self.event_type == 'master':
            context['worker_formset'] = self.make_formset(
                ['Teacher', 'Volunteer',])
        else:
            context['worker_formset'] = self.make_formset(
                ['Staff Lead', 'Teacher', 'Volunteer',])
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickClassForm(
            request.POST,
            initial={'conference':  self.conference})
        context['third_title'] = "Make New Class"
        if 'pick_class' in request.POST.keys() and context[
                'second_form'].is_valid():
            if context['second_form'].cleaned_data[
                    'accepted_class']:
                working_class = context['second_form'].cleaned_data[
                    'accepted_class']
                context['third_title'] = "Book Class:  %s" % (
                    working_class.e_title)
                context['third_form'] = ClassBookingForm(
                    instance=working_class)
                duration = working_class.duration.hours() + float(
                    working_class.duration.minutes())/60
            else:
                context['third_form'] = ClassBookingForm()
            context['scheduling_form'] = ScheduleOccurrenceForm(
                conference=self.conference,
                open_to_public=True,
                initial={'duration': duration, })
            context['scheduling_form'].fields[
                'max_volunteer'].widget = HiddenInput()
            WorkerFormSet, initial = self.make_formset(working_class)
            context['worker_formset'] = WorkerFormSet(
                initial=initial)

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
            WorkerFormSet, initial = self.make_formset(working_class)
            context['worker_formset'] = WorkerFormSet(request.POST)
            if context['third_form'].is_valid(
                    ) and context['scheduling_form'].is_valid(
                    ) and context['worker_formset'].is_valid():
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
