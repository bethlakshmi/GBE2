from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.forms import formset_factory
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import (
    ClassBookingForm,
    PickClassForm,
    ScheduleOccurrenceForm,
    PersonAllocationForm,
)
from gbe.models import (
    Class,
    Room,
)
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
    validate_perms
)
from gbe.scheduling.views import EventWizardView
from functools import partial, wraps
from gbe.scheduling.views.functions import (
    get_start_time,
    show_scheduling_occurrence_status,
)
from scheduler.data_transfer import Person
from scheduler.idd import create_occurrence
from gbe.duration import Duration


class ClassWizardView(EventWizardView):
    template = 'gbe/scheduling/class_wizard.tmpl'
    roles = ['Teacher', 'Volunteer', 'Moderator', 'Panelist', ]
    default_event_type = "conference"


    def groundwork(self, request, args, kwargs):
        context = super(ClassWizardView,
                        self).groundwork(request, args, kwargs)
        context['event_type'] = "Conference Class"
        context['second_title'] = "Pick the Class"
        return context

    def book_event(self, scheduling_form, people_formset, working_class):
        room = get_object_or_404(Room, name=scheduling_form.cleaned_data['location'])
        max_volunteer = 0
        start_time = get_start_time(scheduling_form.cleaned_data)
        labels = [self.conference.conference_slug]
        if working_class.calendar_type:
                labels += [working_class.calendar_type]
        people = []
        for assignment in people_formset:
            if assignment.cleaned_data[
                    'role'] in self.roles and assignment.cleaned_data['worker']:
                people += [Person(
                    user=assignment.cleaned_data['worker'].workeritem.as_subtype.user_object,
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

    def make_formset(self, working_class):
        if working_class.type == 'Panel':
            WorkerFormSet = formset_factory(wraps(
                PersonAllocationForm)(partial(
                PersonAllocationForm,
                label_visible=False,
                role_options=[
                    ('Panelist', 'Panelist'),
                    ('Moderator', 'Moderator')],
                use_personas=True,)), extra=3, can_delete=True)
            initial=[{'worker': working_class.teacher,
                      'role': 'Moderator'}]
        else:
            WorkerFormSet = formset_factory(wraps(
                PersonAllocationForm)(partial(
                PersonAllocationForm,
                label_visible=False,
                role_options=[
                    ('Teacher', 'Teacher'),
                    ('Volunteer', 'Volunteer')],
                use_personas=True,)), extra=1, can_delete=True)
            initial=[{'worker': working_class.teacher,
                      'role': 'Teacher'}]
        return (WorkerFormSet, initial)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickClassForm(
            initial={'conference':  self.conference})
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickClassForm(
            request.POST,
            initial={'conference':  self.conference})
        if 'pick_class' in request.POST.keys() and context[
                'second_form'].is_valid():
            working_class = context['second_form'].cleaned_data[
                'accepted_class']
            context['third_form'] = ClassBookingForm(
                instance=working_class)
            context['scheduling_form'] = ScheduleOccurrenceForm(
                conference=self.conference,
                open_to_public=True,
                initial={'duration': working_class.duration.hours() + float(
                    working_class.duration.minutes())/60,})
            context['scheduling_form'].fields[
                'max_volunteer'].widget = HiddenInput()
            WorkerFormSet, initial = self.make_formset(working_class)
            context['worker_formset'] = WorkerFormSet(
                initial=initial)

        elif 'set_class' in request.POST.keys(
                ) and 'eventitem_id' in request.POST.keys():
            working_class = get_object_or_404(
                Class,
                eventitem_id=request.POST['eventitem_id'])
            context['second_form'] = PickClassForm(
                initial={'conference':  self.conference,
                         'accepted_class': working_class})
            context['third_form'] = ClassBookingForm(request.POST,
                                                     instance=working_class)
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
                response = self.book_event(context['scheduling_form'],
                                context['worker_formset'],
                                working_class)                
                if response.occurrence:
                    update_class = context['third_form'].save(commit=False)
                    update_class.duration = Duration(
                        minutes=context['scheduling_form'].cleaned_data['duration']*60)
                    update_class.save()
                show_scheduling_occurrence_status(
                    request,
                    response,
                    self.__class__.__name__)
                if response.occurrence:
                    return HttpResponseRedirect(
                        "%s?%s-day=%d&filter=Filter&new=%d" % (
                            reverse('manage_event_list',
                                    urlconf='gbe.scheduling.urls',
                                    args=[self.conference.conference_slug]),
                            self.conference.conference_slug,
                            context['scheduling_form'].cleaned_data['day'].pk,
                            response.occurrence.pk,))
            context['third_title'] = "Book Class:  %s" % working_class.e_title
        return render(request, self.template, context)
