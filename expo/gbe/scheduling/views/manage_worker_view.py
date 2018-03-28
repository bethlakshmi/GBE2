from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.forms import HiddenInput
from django.contrib import messages
from scheduler.idd import (
    create_occurrence,
    get_conflicts,
    get_occurrence,
    get_occurrences,
    update_occurrence,
)
from gbe.models import (
    Profile,
    GenericEvent,
    Room,
    UserMessage,
)
from gbe.scheduling.forms import WorkerAllocationForm
from gbe.scheduling.views.functions import (
    get_start_time,
    show_scheduling_occurrence_status,
)
from gbe.functions import eligible_volunteers
from gbe_forms_text import rank_interest_options

class ManageWorkerView(View):
    ''' This must be a parent to another class.  The subclass should describe
        the settings and visualization for the volunteer event being staffed
        here.   The contract for the child is to implement a 'groundwork'
        function and provide:
        REQUIRED
            - self.conference - the conference for which the vol opp is being
                managed
            - any additional self.labels (a list) to be used during opp create
                - the conference slug, and appropriate calendar type will be
                made here.
            - self.manage_worker_url - the URL used to call this post function
            - self.parent_id (optional) - the id of a parent event, if null,
                there will be no parent
            - self.success_url - the URL to redirect to in the event of success
            - 'make_context' to build the error context when an error occurrs
        OPTIONAL
            - do_additional_actions - to provide additional opps related
            actions - if not provide, edit, create, delete, duplicate are
            available, if one of those functions is not provided, post will
            exit with no return value
            - window_controls = list of controls for panels in the page, if
            adding panels, include turning them on and off via the errorcontext
            and the request.GET parameters.  If no panels are on, all panels
            will be opened.
    '''

    vol_permissions = ('Volunteer Coordinator',)
    parent_id = None
    labels = []
    window_controls = ['start_open', 'worker_open']

    def make_context(self, request, errorcontext=None):
        context = {}
        vol_open = False
        all_closed = True

        if errorcontext is not None:
            context = errorcontext
        context['edit_url'] = self.success_url

        for window_control in self.window_controls:
            if ((errorcontext and window_control in errorcontext
                 ) and errorcontext[window_control]) or request.GET.get(
                    window_control,
                    False) in ["True", "true", "T", "t", True]:
                context[window_control] = True
                all_closed = False

        if all_closed:
            for window_control in self.window_controls:
                context[window_control] = True

        return context

    def get_worker_allocation_forms(self, errorcontext=None):
        '''
        Returns a list of allocation forms for a volunteer opportunity
        Each form can be used to schedule one worker. Initially, must
        allocate one at a time.
        '''
        forms = []
        for person in self.occurrence.people:
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
                'manage_worker_url': self.manage_worker_url}

    def get_volunteer_info(self):
        volunteer_set = []
        for volunteer in eligible_volunteers(
                self.occurrence.start_time,
                self.occurrence.end_time,
                self.item.e_conference):
            assign_form = WorkerAllocationForm(
                initial={'role': 'Volunteer',
                         'worker': volunteer.profile,
                         'alloc_id': -1})
            assign_form.fields['worker'].widget = HiddenInput()
            assign_form.fields['label'].widget = HiddenInput()
            if volunteer.volunteerinterest_set.filter(
                        interest=self.occurrence.as_subtype.volunteer_type
                        ).exists():
                rank = volunteer.volunteerinterest_set.get(
                        interest=self.occurrence.as_subtype.volunteer_type).rank
            else:
                rank = 0
            conflict_response = get_conflicts(
                self.occurrence,
                volunteer.profile.user_object,
                labels=[self.conference.conference_slug])
            
            conflicts = None
            if hasattr(conflict_response, 'occurrences'):
                conflicts = conflict_response.occurrences

            volunteer_set += [{
                'display_name': volunteer.profile.display_name,
                'interest': rank_interest_options[rank],
                'available': volunteer.check_available(
                    self.occurrence.start_time,
                    self.occurrence.end_time),
                'conflicts': conflicts,
                'id': volunteer.pk,
                'assign_form': assign_form
            }]
        return {'eligible_volunteers': volunteer_set}

    def make_post_response(self,
                           request,
                           response=None,
                           errorcontext=None):
        if response:
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)

        if response and response.occurrence:
            return HttpResponseRedirect(self.success_url)
        else:
            return render(request,
                          self.template,
                          self.make_context(request, errorcontext))

    def check_success_and_return(self,
                                 request,
                                 response=None,
                                 errorcontext=None,
                                 window_controls="worker_open=True"):
        if response and response.occurrence:
            self.success_url = "%s?changed_id=%d" % (
                self.success_url,
                response.occurrence.pk)
            if window_controls:
                self.success_url = "%s&%s" % (self.success_url,
                                              window_controls)

        return self.make_post_response(
            request,
            response,
            errorcontext)

    def get_basic_form_settings(self):
        self.event = self.event_form.save(commit=False)
        data = self.event_form.cleaned_data
        self.room = get_object_or_404(Room, name=data['location'])
        self.max_volunteer = 0
        if data['max_volunteer']:
                self.max_volunteer = data['max_volunteer']
        self.start_time = get_start_time(data)
        if self.create:
            data['labels'] = self.labels + [self.conference.conference_slug]
            if self.event.calendar_type:
                data['labels'] += [self.event.calendar_type]
        return data

    def do_additional_actions(self, request):
        return None

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        self.create = False
        response = None
        context = None

        if ('create' in request.POST.keys()) or (
                'duplicate' in request.POST.keys()):
            self.create = True
            if 'create' in request.POST.keys():
                self.event_form = VolunteerOpportunityForm(
                    request.POST,
                    prefix='new_opp',
                    conference=self.conference)
            else:
                self.event_form = VolunteerOpportunityForm(
                    request.POST,
                    conference=self.conference)
            if self.event_form.is_valid():
                data = self.get_basic_form_settings()
                self.event.e_conference = self.conference
                self.event.save()
                response = create_occurrence(
                    self.event.eventitem_id,
                    self.start_time,
                    self.max_volunteer,
                    locations=[self.room],
                    labels=data['labels'],
                    parent_event_id=self.parent_id)
            else:
                context = {'createform': self.event_form,
                           'worker_open': True}

            return self.check_success_and_return(request,
                                                 response=response,
                                                 errorcontext=context)

        elif 'edit' in request.POST.keys():
            self.event = get_object_or_404(
                GenericEvent,
                event_id=request.POST['opp_event_id'])
            self.event_form = VolunteerOpportunityForm(
                request.POST,
                instance=self.event)
            if self.event_form.is_valid():
                data = self.get_basic_form_settings()
                self.event_form.save()
                response = update_occurrence(
                    data['opp_sched_id'],
                    self.start_time,
                    self.max_volunteer,
                    locations=[self.room])
            else:
                context = {'error_opp_form': self.event_form,
                           'worker_open': True}

            return self.check_success_and_return(request,
                                                 response=response,
                                                 errorcontext=context)

        elif 'delete' in request.POST.keys():
            opp = get_object_or_404(
                GenericEvent,
                event_id=request.POST['opp_event_id'])
            title = opp.e_title
            opp.delete()
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DELETE_SUCCESS",
                defaults={
                    'summary': "Volunteer Opportunity Deleted",
                    'description': "This volunteer opportunity was deleted."})
            messages.success(
                request,
                '%s<br>Title: %s' % (
                    user_message[0].description,
                    title))
            return HttpResponseRedirect(self.success_url)

        elif 'allocate' in request.POST.keys():
            response = get_occurrence(request.POST['opp_sched_id'])
            return HttpResponseRedirect(
                reverse('edit_event_schedule',
                        urlconf='gbe.scheduling.urls',
                        args=['GenericEvent',
                              response.occurrence.eventitem.eventitem_id,
                              request.POST['opp_sched_id']]))
        else:
            actions = self.do_additional_actions(request)
            if actions:
                return actions
            else:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="UNKNOWN_ACTION",
                    defaults={
                        'summary': "Unknown Action",
                        'description': "This is an unknown action."})
                messages.error(
                    request,
                    user_message[0].description)
                return HttpResponseRedirect(self.success_url)
