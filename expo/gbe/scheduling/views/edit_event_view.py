from gbe.scheduling.views import ManageVolWizardView
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
)
from gbe.duration import Duration
from gbe.functions import (
    get_conference_day,
    validate_perms
)
from gbe_forms_text import (
    role_map,
    event_settings,
)
from scheduler.idd import (
    get_occurrence,
    update_occurrence,
)
from scheduler.data_transfer import Person
from gbe.scheduling.views.functions import (
    get_start_time,
    show_scheduling_occurrence_status,
)


class EditEventView(ManageVolWizardView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        if "conference" in kwargs:
            self.conference = get_object_or_404(
                Conference,
                conference_slug=kwargs['conference'])

        if "occurrence_id" in kwargs:
            self.parent_id = int(kwargs['occurrence_id'])
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
        self.manage_vol_url = reverse('manage_vol',
                                      urlconf='gbe.scheduling.urls',
                                      args=[kwargs['conference'],
                                            kwargs['occurrence_id']])
        self.success_url = reverse('edit_event',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.conference.conference_slug,
                                         self.occurrence.pk])

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

    def make_context(self, request, errorcontext=None):
        context = {
            'edit_title':  'Edit Event'
        }
        if errorcontext is not None:
            context = errorcontext
        duration = float(self.item.duration.total_minutes())/60
        initial_form_info = {
                'duration': duration,
                'max_volunteer': self.occurrence.max_volunteer,
                'day': get_conference_day(
                    conference=self.conference,
                    date=self.occurrence.starttime.date()),
                'time': self.occurrence.starttime.strftime("%H:%M:%S"),
                'location': self.occurrence.location,
                'occurrence_id': self.occurrence.pk, }
        context['event_id'] = self.occurrence.pk
        context['eventitem_id'] = self.item.eventitem_id

        # if there was an error in the edit form
        if 'event_form' not in context:
            context['event_form'] = EventBookingForm(
                    instance=self.item)
        if 'scheduling_form' not in context:
            context['scheduling_form'] = ScheduleOccurrenceForm(
                conference=self.conference,
                open_to_public=True,
                initial=initial_form_info)

        if 'worker_formset' not in context:
            context['worker_formset'] = self.make_formset(
                event_settings[self.item.type.lower()]['roles'])

        if validate_perms(request,
                          ('Volunteer Coordinator',), require=False):
            volunteer_initial_info = initial_form_info.copy()
            volunteer_initial_info.pop('occurrence_id')
            volunteer_initial_info['duration'] = self.item.duration
            context.update(super(EditEventView,
                                 self).get_manage_opportunity_forms(
                volunteer_initial_info,
                self.manage_vol_url,
                self.conference,
                request,
                errorcontext=errorcontext,
                occurrence_id=self.occurrence.pk))
        else:
            context['edit_open'] = True

        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url

        return self.make_context(request)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        if "manage-opps" in request.path:
            return super(EditEventView, self).post(request, *args, **kwargs)
        context = {}
        response = None
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
            if request.POST.get('edit_event', 0) != "Save and Continue":
                self.success_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
                    reverse('manage_event_list',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    self.conference.conference_slug,
                    context['scheduling_form'].cleaned_data['day'].pk,
                    str([self.occurrence.pk]),)
            else:
                self.success_url = request.path
        else:
            context['edit_open'] = True
        return self.make_post_response(request,
                                       response=response,
                                       errorcontext=context)
