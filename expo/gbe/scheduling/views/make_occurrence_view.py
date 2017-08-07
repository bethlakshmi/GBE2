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
from gbe.scheduling.forms import ScheduleSelectionForm
from scheduler.idd import (
    create_occurrence,
    edit_occurrence,
    get_occurrence
)
from scheduler.views.functions import (
    get_event_display_info,
)
from scheduler.views import (
    get_manage_opportunity_forms,
    get_worker_allocation_forms,
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
from scheduler.forms import WorkerAllocationForm
from gbe_forms_text import (
    rank_interest_options,
)


class MakeOccurrenceView(View):
    template = 'scheduler/event_schedule.tmpl'
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

    def groundwork(self, request, args, kwargs):
        eventitem_id = kwargs['eventitem_id']
        self.event_type = kwargs['event_type'] or 'Class'
        self.profile = validate_perms(request, ('Scheduling Mavens',))
        try:
            self.item = Event.objects.get_subclass(pk=eventitem_id)
        except Event.DoesNotExist:
            raise Http404
        self.eventitem_view = get_event_display_info(eventitem_id)
        if "occurrence_id" in kwargs:
            result = get_occurrence(kwargs['occurrence_id'])
            if result.errors and len(result.errors) > 0:
                raise Exception("broken!")
            else:
                self.occurrence = result.occurrence

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
            volunteer_set += [{
                'display_name': volunteer.profile.display_name,
                'interest': rank_interest_options[
                    volunteer.volunteerinterest_set.get(
                        interest=opp.as_subtype.volunteer_type).rank],
                'available': volunteer.check_available(
                    opp.start_time,
                    opp.end_time),
                'conflicts': volunteer.profile.get_conflicts(opp),
                'id': volunteer.pk,
                'assign_form': assign_form
            }]

        return {'eligible_volunteers': volunteer_set}

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        scheduling_info = {}
        initial_form_info = {}

        context = {'eventitem': self.eventitem_view,
                   'user_id': request.user.id,
                   'event_type': self.event_type,
                   'scheduling_info': get_scheduling_info(self.item),
                   }
        if self.occurrence:
            context['event_id'] = self.occurrence.pk
            initial_form_info['day'] = get_conference_day(
                conference=self.occurrence.eventitem.get_conference(),
                date=self.occurrence.starttime.date())
            initial_form_info['time'] = self.occurrence.starttime.strftime("%H:%M:%S")
            initial_form_info['max_volunteer'] = self.occurrence.max_volunteer
            initial_form_info['location'] = self.occurrence.location
            panelists = []
            for person in self.occurrence.people:
                if person.role:
                    if person.role == "Panelist":
                        panelists +=[person.public_id]
                    elif self.role_key.has_key(person.role):
                        initial_form_info[self.role_key[person.role]] = eval(
                            self.role_class[person.role]).objects.get(pk=person.public_id)
            initial_form_info['panelists'] = panelists
        else:
            initial_form_info['location'] = self.item.default_location

            if self.item.__class__.__name__ == 'Class':
                initial_form_info['teacher'] = self.item.teacher
                initial_form_info['duration'] = Duration(
                    self.item.duration.days,
                    self.item.duration.seconds)

        context['form'] = ScheduleSelectionForm(
            prefix='event',
            instance=self.item,
            initial=initial_form_info)

        if validate_perms(request,
                          ('Volunteer Coordinator',), require=False
                          ) and self.occurrence:
            if (self.item.__class__.__name__ == 'GenericEvent' and
                    self.item.type == 'Volunteer'):
                context.update(get_worker_allocation_forms(self.occurrence))
                context.update(self.get_volunteer_info(self.occurrence))
            else:
                context.update(get_manage_opportunity_forms(self.occurrence,
                                                            initial_form_info))
                if len(context['actionform']) > 0 and request.GET.get(
                        'changed_id', None):
                    context['changed_id'] = int(
                        request.GET.get('changed_id', None))

        return render(
            request,
            self.template,
            context)

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        event_form = ScheduleSelectionForm(
            request.POST,
            instance=self.item,
            prefix='event')
        if event_form.is_valid():
            event = event_form.save(commit=False)
            data = event_form.cleaned_data

            room = get_object_or_404(Room, name=data['location'])
            people = get_single_role(data)
            people += get_multi_role(data)
            max_volunteer = 0
            if data['max_volunteer']:
                max_volunteer = data['max_volunteer']
            start_time = get_start_time(data)
            labels = [event.e_conference.conference_slug]
            if event.calendar_type:
                labels += [event.calendar_type]
            response = create_occurrence(
                event.eventitem_id,
                start_time,
                max_volunteer,
                people=people,
                locations=[room],
                labels=labels)
            if response.occurrence:
                event_form.save()
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)
            return HttpResponseRedirect(reverse('event_schedule',
                                                urlconf='scheduler.urls',
                                                args=[self.event_type]))
        else:
            return render(
                request,
                self.template,
                {'eventitem': self.eventitem_view,
                 'form': event_form,
                 'user_id': request.user.id,
                 'event_type': self.event_type})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MakeOccurrenceView, self).dispatch(*args, **kwargs)
