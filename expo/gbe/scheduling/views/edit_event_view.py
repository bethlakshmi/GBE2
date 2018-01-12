from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from gbe.models import (
    Conference,
    Event,
    Room,
)
from gbe.scheduling.forms import (
    EventBookingForm,
    PersonAllocationForm,
    ScheduleOccurrenceForm,
    VolunteerOpportunityForm,
)
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
    validate_perms
)
from gbe_forms_text import (
    role_map,
    event_settings,
)
from scheduler.idd import (
    get_occurrence,
    get_occurrences,
    update_occurrence,
)
from scheduler.data_transfer import Person
from gbe.scheduling.views.functions import (
    get_start_time,
    show_scheduling_occurrence_status,
)


class EditEventView(View):
    template = 'gbe/scheduling/edit_event.tmpl'

    def groundwork(self, request, args, kwargs):
        if "conference" in kwargs:
            self.conference = get_object_or_404(
                Conference,
                conference_slug=kwargs['conference'])
        if "occurrence_id" in kwargs:
            result = get_occurrence(int(kwargs['occurrence_id']))
            if result.errors and len(result.errors) > 0:
                show_scheduling_occurrence_status(
                    request,
                    result,
                    self.__class__.__name__)
                error_url = reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug])

                return HttpResponseRedirect(error_url)
            else:
                self.occurrence = result.occurrence
        self.item = get_object_or_404(
            Event,
            eventitem_id=self.occurrence.foreign_event_id).child()

    def make_formset(self, roles, post=None):
        formset = []
        n = 0
        for booking in self.occurrence.people:
            formset += [PersonAllocationForm(
                post,
                label_visible=False,
                role_options=[(booking.role, booking.role), ],
                use_personas=role_map[booking.role],
                initial={
                    'role': booking.role,
                    'worker': booking.public_id,
                },
                prefix="alloc_%d" % n)]
            n = n + 1
        for role in roles:
            formset += [PersonAllocationForm(
                post,
                label_visible=False,
                role_options=[(role, role), ],
                use_personas=role_map[role],
                initial={'role': role},
                prefix="alloc_%d" % n), ]
            n = n + 1
        return formset

    def update_event(self, scheduling_form, people_formset, working_class):
        room = get_object_or_404(
            Room,
            name=scheduling_form.cleaned_data['location'])
        start_time = get_start_time(scheduling_form.cleaned_data)
        people = []
        for assignment in people_formset:
            if assignment.is_valid() and assignment.cleaned_data['worker']:
                people += [Person(
                    user=assignment.cleaned_data[
                        'worker'].workeritem.as_subtype.user_object,
                    public_id=assignment.cleaned_data['worker'].workeritem.pk,
                    role=assignment.cleaned_data['role'])]
        response = update_occurrence(
                self.occurrence.pk,
                start_time,
                scheduling_form.cleaned_data['max_volunteer'],
                people=people,
                locations=[room])
        return response

    def is_formset_valid(self, formset):
        validity = False
        for form in formset:
            validity = form.is_valid() or validity
        return validity

    def get_manage_opportunity_forms(self,
                                     initial,
                                     occurrence_id,
                                     errorcontext=None):
        '''
        Generate the forms to allocate, edit, or delete volunteer
        opportunities associated with a scheduler event.
        '''
        actionform = []
        context = {}
        response = get_occurrences(parent_event_id=occurrence_id)
        for vol_occurence in response.occurrences:
            vol_event = Event.objects.get_subclass(
                    eventitem_id=vol_occurence.foreign_event_id)
            if (errorcontext and
                    'error_opp_form' in errorcontext and
                    errorcontext['error_opp_form'].instance == vol_event):
                actionform.append(errorcontext['error_opp_form'])
            else:
                num_volunteers = vol_occurence.max_volunteer
                date = vol_occurence.start_time.date()

                time = vol_occurence.start_time.time
                day = get_conference_day(
                    conference=vol_event.e_conference,
                    date=date)
                location = vol_occurence.location
                if location:
                    room = location.room
                elif self.occurrence.location:
                    room = self.occurrence.location.room

                actionform.append(
                    VolunteerOpportunityForm(
                        instance=vol_event,
                        initial={'opp_event_id': vol_event.event_id,
                                 'opp_sched_id': vol_occurence.id,
                                 'max_volunteer': num_volunteers,
                                 'day': day,
                                 'time': time,
                                 'location': room,
                                 'type': "Volunteer"
                                 },
                        )
                    )
        context['actionform'] = actionform
        if errorcontext and 'createform' in errorcontext:
            createform = errorcontext['createform']
        else:
            createform = VolunteerOpportunityForm(
                prefix='new_opp',
                initial=initial,
                conference=self.occurrence.eventitem.get_conference())

        actionheaders = ['Title',
                         'Volunteer Type',
                         '#',
                         'Duration',
                         'Day',
                         'Time',
                         'Location']
        context.update({'createform': createform,
                        'actionheaders': actionheaders,
                        'manage_vol_url': "yo"})
        return context

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {}
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        
        duration = float(self.item.duration.total_minutes())/60
        context['event_form'] = EventBookingForm(
                instance=self.item)
        initial_form_info = {
                'duration': duration,
                'max_volunteer': self.occurrence.max_volunteer,
                'day': get_conference_day(
                    conference=self.conference,
                    date=self.occurrence.starttime.date()),
                'time': self.occurrence.starttime.strftime("%H:%M:%S"),
                'location': self.occurrence.location,
                'occurrence_id': self.occurrence.pk,}
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=self.conference,
            open_to_public=True,
            initial=initial_form_info)
        initial_form_info.pop('occurrence_id')
        context['worker_formset'] = self.make_formset(
            event_settings[self.item.type.lower()]['roles'])
        context.update(self.get_manage_opportunity_forms(
            initial_form_info,
            self.occurrence.pk))
        context['event_id'] = self.occurrence.pk
        context['eventitem_id'] = self.item.eventitem_id
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = {}
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        context['event_form'] = EventBookingForm(request.POST,
                                                 instance=self.item)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            request.POST,
            conference=self.conference,
            open_to_public=True,)
        context['worker_formset'] = self.make_formset(
            event_settings[self.item.type.lower()]['roles'],
            post=request.POST)

        if context['event_form'].is_valid(
                ) and context['scheduling_form'].is_valid(
                ) and self.is_formset_valid(context['worker_formset']):
            new_event = context['event_form'].save(commit=False)
            new_event.duration = Duration(
                minutes=context['scheduling_form'].cleaned_data[
                    'duration']*60)
            new_event.save()
            response = self.update_event(context['scheduling_form'],
                                       context['worker_formset'],
                                       new_event)
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)
            if len(response.errors) == 0 and request.POST.get('pick_event', 0) == "Save and Exit":
                return HttpResponseRedirect(
                    "%s?%s-day=%d&filter=Filter&new=%s" % (
                        reverse('manage_event_list',
                                urlconf='gbe.scheduling.urls',
                                args=[self.conference.conference_slug]),
                        self.conference.conference_slug,
                        context['scheduling_form'].cleaned_data['day'].pk,
                        str([self.occurrence.pk]),))
        return render(request, self.template, context)
