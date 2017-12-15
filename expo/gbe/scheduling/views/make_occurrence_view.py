from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import (
    ScheduleSelectionForm,
    VolunteerOpportunityForm,
    WorkerAllocationForm,
)
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    get_occurrences,
    update_occurrence,
)
from gbe.scheduling.views.functions import (
    get_event_display_info,
)
from gbe.scheduling.views.functions import (
    get_single_role,
    get_multi_role,
    get_start_time,
    show_scheduling_occurrence_status,
)
from gbe.models import (
    Event,
    Performer,
    Profile,
    Room,
)
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
    validate_perms
)
from gbe.duration import Duration
from gbe.views.class_display_functions import get_scheduling_info
from gbe_forms_text import (
    rank_interest_options,
)


class MakeOccurrenceView(View):
    template = 'gbe/scheduling/event_schedule.tmpl'
    permissions = ('Scheduling Mavens',)

    role_key = {
        'Staff Lead': 'staff_lead',
        'Moderator': 'moderator',
        'Teacher': 'teacher',
    }

    role_class = {
        'Staff Lead': 'Profile',
        'Moderator': 'Performer',
        'Teacher': 'Performer',
    }
    occurrence = None
    people = []
    event_form = None

    def groundwork(self, request, args, kwargs):
        eventitem_id = kwargs['eventitem_id']
        self.event_type = kwargs['event_type'] or 'Class'
        self.profile = validate_perms(request, self.permissions)
        try:
            self.item = Event.objects.get_subclass(eventitem_id=eventitem_id)
        except Event.DoesNotExist:
            raise Http404
        self.eventitem_view = get_event_display_info(eventitem_id)

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
        response = get_occurrences(occurrence_id)
        for vol_occurence in response.occurrences:
            vol_event = Event.objects.get_subclass(
                pk=vol_occurence.foreign_event_id)
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
                        'actionheaders': actionheaders})
        return context

    def get_worker_allocation_forms(self, opp, errorcontext=None):
        '''
        Returns a list of allocation forms for a volunteer opportunity
        Each form can be used to schedule one worker. Initially, must
        allocate one at a time.
        '''
        forms = []
        for person in opp.people:
            if (errorcontext and
                    'worker_alloc_forms' in errorcontext and
                    errorcontext['worker_alloc_forms'].cleaned_data[
                        'alloc_id'] == person.booking_id):
                forms.append(errorcontext['worker_alloc_forms'])
            else:
                try:
                    forms.append(WorkerAllocationForm(
                        initial={
                            'worker': Profile.objects.get(pk=person.public_id),
                            'role': person.role,
                            'label': person.label,
                            'alloc_id': person.booking_id}))
                except Profile.DoesNotExist:
                    pass
        if errorcontext and 'new_worker_alloc_form' in errorcontext:
            forms.append(errorcontext['new_worker_alloc_form'])
        else:
            forms.append(WorkerAllocationForm(initial={'role': 'Volunteer',
                                                       'alloc_id': -1}))
        return {'worker_alloc_forms': forms,
                'worker_alloc_headers': ['Worker', 'Role', 'Notes'],
                'opp_id': opp.id}

    def get_volunteer_info(self, opp, errorcontext=None):
        volunteer_set = []
        for volunteer in eligible_volunteers(
                opp.start_time,
                opp.end_time,
                self.item.e_conference):
            assign_form = WorkerAllocationForm(
                initial={'role': 'Volunteer',
                         'worker': volunteer.profile,
                         'alloc_id': -1})
            assign_form.fields['worker'].widget = HiddenInput()
            assign_form.fields['label'].widget = HiddenInput()
            if volunteer.volunteerinterest_set.filter(
                        interest=opp.as_subtype.volunteer_type).exists():
                rank = volunteer.volunteerinterest_set.get(
                        interest=opp.as_subtype.volunteer_type).rank
            else:
                rank = 0
            volunteer_set += [{
                'display_name': volunteer.profile.display_name,
                'interest': rank_interest_options[rank],
                'available': volunteer.check_available(
                    opp.start_time,
                    opp.end_time),
                'conflicts': volunteer.profile.get_conflicts(opp),
                'id': volunteer.pk,
                'assign_form': assign_form
            }]

        return {'eligible_volunteers': volunteer_set}

    def make_context(self, request, occurrence_id=None, errorcontext=None):
        initial_form_info = {}
        scheduling_info = {}
        if occurrence_id:
            result = get_occurrence(occurrence_id)
            if result.errors and len(result.errors) > 0:
                show_scheduling_occurrence_status(
                    request,
                    result,
                    self.__class__.__name__)
                error_url = reverse(
                    'event_schedule',
                    urlconf='scheduler.urls',
                    args=[self.event_type])
                return HttpResponseRedirect(error_url)

            else:
                self.occurrence = result.occurrence

        context = {'eventitem': self.eventitem_view,
                   'user_id': request.user.id,
                   'event_type': self.event_type,
                   'scheduling_info': get_scheduling_info(self.item),
                   }
        if self.occurrence:
            context['event_id'] = self.occurrence.pk
            context['eventitem_id'] = self.occurrence.foreign_event_id
            initial_form_info['day'] = get_conference_day(
                conference=self.item.get_conference(),
                date=self.occurrence.starttime.date())
            initial_form_info['time'] = self.occurrence.starttime.strftime(
                "%H:%M:%S")
            initial_form_info['max_volunteer'] = self.occurrence.max_volunteer
            initial_form_info['location'] = self.occurrence.location
            panelists = []
            for person in self.occurrence.people:
                if person.role:
                    if person.role == "Panelist":
                        panelists += [person.public_id]
                    elif person.role in self.role_key:
                        try:
                            initial_form_info[
                                self.role_key[person.role]] = eval(
                                self.role_class[person.role]
                                ).objects.get(pk=person.public_id)
                        except Performer.DoesNotExist:
                            initial_form_info[
                                self.role_key[person.role]
                                ] = Profile.objects.get(
                                pk=person.public_id)
            initial_form_info['panelists'] = panelists
        else:
            initial_form_info['location'] = self.item.default_location

            if self.item.__class__.__name__ == 'Class':
                initial_form_info['teacher'] = self.item.teacher
                initial_form_info['duration'] = Duration(
                    self.item.duration.days,
                    self.item.duration.seconds)
        if errorcontext and ('form' in errorcontext):
            context['form'] = errorcontext['form']
        else:
            context['form'] = ScheduleSelectionForm(
                prefix='event',
                instance=self.item,
                initial=initial_form_info)

        if validate_perms(request,
                          ('Volunteer Coordinator',), require=False
                          ) and self.occurrence:
            if (self.item.__class__.__name__ == 'GenericEvent' and
                    self.item.type == 'Volunteer'):
                context.update(
                    self.get_worker_allocation_forms(self.occurrence,
                                                     errorcontext))
                context.update(self.get_volunteer_info(self.occurrence))
            else:
                initial_form_info['duration'] = self.item.duration
                context.update(
                    self.get_manage_opportunity_forms(initial_form_info,
                                                      occurrence_id,
                                                      errorcontext))
            if self.request.GET.get('changed_id', None):
                context['changed_id'] = int(
                    self.request.GET.get('changed_id', None))

        return render(
            request,
            self.template,
            context)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        occurrence_id = None
        if "occurrence_id" in kwargs:
            occurrence_id = int(kwargs['occurrence_id'])

        return self.make_context(request, occurrence_id)

    def get_basic_form_settings(self):
        self.event = self.event_form.save(commit=False)
        data = self.event_form.cleaned_data
        self.room = get_object_or_404(Room, name=data['location'])
        self.max_volunteer = 0
        if data['max_volunteer']:
                self.max_volunteer = data['max_volunteer']
        self.start_time = get_start_time(data)
        if self.create:
            self.labels = [self.item.e_conference.conference_slug]
            if self.event.calendar_type:
                self.labels += [self.event.calendar_type]

        return data

    def make_post_response(self,
                           request,
                           response=None,
                           occurrence_id=None,
                           errorcontext=None):
        if response:
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)

        if response and response.occurrence:
            return HttpResponseRedirect(self.success_url)
        else:
            return self.make_context(request, occurrence_id, errorcontext)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        success = False
        response = None
        context = None
        self.event_form = ScheduleSelectionForm(
            request.POST,
            instance=self.item,
            prefix='event')
        occurrence_id = None
        self.create = True
        if "occurrence_id" in kwargs:
            occurrence_id = int(kwargs['occurrence_id'])
            self.create = False

        if self.event_form.is_valid():
            data = self.get_basic_form_settings()
            people = get_single_role(data)
            people += get_multi_role(data)

            if self.create:
                response = create_occurrence(
                    self.event.eventitem_id,
                    self.start_time,
                    self.max_volunteer,
                    people=people,
                    locations=[self.room],
                    labels=self.labels)
                self.success_url = reverse(
                    'event_schedule',
                    urlconf='scheduler.urls',
                    args=[self.event_type])
            else:
                response = update_occurrence(
                    int(kwargs['occurrence_id']),
                    self.start_time,
                    self.max_volunteer,
                    people=people,
                    roles=["Teacher", "Staff Lead", "Moderator", "Panelist"],
                    locations=[self.room])
                self.success_url = reverse(
                    'edit_event_schedule',
                    urlconf='gbe.scheduling.urls',
                    args=[self.event_type,
                          self.item.eventitem_id,
                          int(kwargs['occurrence_id'])])
            if response.occurrence:
                self.event_form.save()
        else:
            context = {'form': self.event_form}

        return self.make_post_response(request,
                                       response=response,
                                       occurrence_id=occurrence_id,
                                       errorcontext=context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MakeOccurrenceView, self).dispatch(*args, **kwargs)
