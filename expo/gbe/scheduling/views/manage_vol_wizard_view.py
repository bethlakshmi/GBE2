from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    get_occurrences,
    update_occurrence,
)
from gbe.models import (
    Event,
    GenericEvent,
    Room,
)
from django.views.generic import View
from gbe.scheduling.forms import VolunteerOpportunityForm
from gbe.scheduling.views.functions import (
    get_start_time,
)
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
)


class ManageVolWizardView(View):
    ''' This must be a parent to another class.  The subclass should describe
        the settings and visualization for the parent of the volunteer events
        manipulated here.   The contract for the child includes:
           - implement a 'groundwork' function and provide self.conference,
              any container related self.labels (a list) and if applicable,
              self.parent_id
           - implement a make_post_reponse that accomodates the errorcontext
              provided here and uses the self.success_url
    '''

    vol_permissions = ('Volunteer Coordinator',)
    parent_id = None

    def get_manage_opportunity_forms(self,
                                     initial,
                                     manage_vol_info,
                                     conference,
                                     errorcontext=None,
                                     occurrence_id=None,
                                     labels=[]):
        '''
        Generate the forms to allocate, edit, or delete volunteer
        opportunities associated with a scheduler event.
        '''
        actionform = []
        context = {}
        if occurrence_id is not None:
            response = get_occurrences(parent_event_id=occurrence_id)
        elif len(labels) > 0:
            response = get_occurrences(labels=labels)
        else:
            return None

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
                                 'opp_sched_id': vol_occurence.pk,
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
                conference=conference)

        actionheaders = ['Title',
                         'Volunteer Type',
                         '#',
                         'Duration',
                         'Day',
                         'Time',
                         'Location']
        context.update({'createform': createform,
                        'actionheaders': actionheaders,
                        'manage_vol_url': manage_vol_info}),
        return context

    def check_success_and_return(self,
                           request,
                           response=None,
                           errorcontext=None):
        self.success_url = reverse('edit_event',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.conference.conference_slug,
                                         self.occurrence.pk])
        if response and response.occurrence:
            self.success_url = "%s?changed_id=%d" % (
                self.success_url,
                response.occurrence.pk)
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
            self.labels = [self.conference.conference_slug]
            if self.event.calendar_type:
                self.labels += [self.event.calendar_type]
        return data

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
                    conference=self.item.get_conference())
            else:
                self.event_form = VolunteerOpportunityForm(
                    request.POST,
                    conference=self.item.get_conference())
            if self.event_form.is_valid():
                data = self.get_basic_form_settings()
                self.event.e_conference = self.item.get_conference()
                self.event.save()
                response = create_occurrence(
                    self.event.eventitem_id,
                    self.start_time,
                    self.max_volunteer,
                    locations=[self.room],
                    labels=self.labels,
                    parent_event_id=self.parent_id)
            else:
                context = {'createform': self.event_form}

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
                context = {'error_opp_form': self.event_form}

            return self.check_success_and_return(request,
                                                 response=response,
                                                 errorcontext=context)

        elif 'delete' in request.POST.keys():
            opp = get_object_or_404(
                GenericEvent,
                event_id=request.POST['opp_event_id'])
            opp.delete()
            return HttpResponseRedirect(
                reverse('edit_event',
                        urlconf='gbe.scheduling.urls',
                        args=[kwargs['conference'],
                              kwargs['occurrence_id']]))

        elif 'allocate' in request.POST.keys():
            response = get_occurrence(request.POST['opp_sched_id'])
            return HttpResponseRedirect(
                reverse('edit_event_schedule',
                        urlconf='gbe.scheduling.urls',
                        args=['GenericEvent',
                              response.occurrence.eventitem.eventitem_id,
                              request.POST['opp_sched_id']]))
