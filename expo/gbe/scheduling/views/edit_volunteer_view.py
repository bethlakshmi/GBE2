from gbe.scheduling.views import ManageWorkerView
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
from gbe.functions import validate_perms
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
    setup_event_management_form,
    show_scheduling_occurrence_status,
    shared_groundwork,
)


class EditVolunteerView(ManageWorkerView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)
    title = "Edit Volunteer Opportunity"

    def groundwork(self, request, args, kwargs):
        groundwork_data = shared_groundwork(request, kwargs, self.permissions)
        if groundwork_data is None:
            error_url = reverse('manage_event_list',
                                urlconf='gbe.scheduling.urls',
                                args=[kwargs['conference']])
            return HttpResponseRedirect(error_url)
        else:
            (self.profile, self.occurrence, self.item) = groundwork_data
            self.conference = self.item.e_conference
        if self.item.type != "Volunteer":
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_event',
                        urlconf='gbe.scheduling.urls',
                        args=[self.item.e_conference.conference_slug,
                              self.occurrence.pk]),
                request.GET.urlencode()))
        self.manage_worker_url = reverse('manage_workers',
                                         urlconf='gbe.scheduling.urls',
                                         args=[self.item.e_conference.conference_slug,
                                               self.occurrence.pk])
        self.success_url = reverse('edit_volunteer',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.item.e_conference.conference_slug,
                                         self.occurrence.pk])

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
        context = super(EditVolunteerView,
                        self).make_context(request, errorcontext)
        context, initial_form_info = setup_event_management_form(
            self.item.e_conference,
            self.item,
            self.occurrence,
            context)
        context['edit_title'] = self.title

        if validate_perms(request,
                          ('Volunteer Coordinator',),
                          require=False):
            volunteer_initial_info = initial_form_info.copy()
            volunteer_initial_info.pop('occurrence_id')
            volunteer_initial_info['duration'] = self.item.duration
            context.update(self.get_manage_opportunity_forms(
                volunteer_initial_info,
                self.manage_worker_url,
                self.conference,
                request,
                errorcontext=errorcontext,
                occurrence_id=self.occurrence.pk))
        else:
            context['start_open'] = True

        return context

    def is_manage_opps(self, path):
        return "manage-opps" in path

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        return render(request, self.template, self.make_context(request))

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if self.is_manage_opps(request.path):
            return super(EditVolunteerView, self).post(request, *args, **kwargs)
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        context = {}
        response = None
        context['event_form'] = EventBookingForm(request.POST,
                                                 instance=self.item)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            request.POST,
            conference=self.conference,
            open_to_public=True,)

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
                self.success_url = "%s?volunteer_open=True" % self.success_url
        else:
            context['start_open'] = True
        return self.make_post_response(request,
                                       response=response,
                                       errorcontext=context)
