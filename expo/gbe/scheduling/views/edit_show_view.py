from gbe.scheduling.views import EditEventView
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
    GenericEvent,
    Room,
)
from gbe.scheduling.forms import RehearsalSlotForm
from gbe.duration import Duration
from gbe.functions import (
    get_conference_day,
    validate_perms
)
from gbe_forms_text import (
    role_map,
    event_settings,
)
from gbetext import rehearsal_delete_msg
from scheduler.idd import (
    get_occurrences,
    create_occurrence,
)
from scheduler.data_transfer import Person
from gbe.scheduling.views.functions import (
    get_start_time,
    show_scheduling_occurrence_status,
)
from datetime import timedelta


class EditShowView(EditEventView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)
    title = "Edit Show"

    def groundwork(self, request, args, kwargs):
        error_url = super(EditShowView,
                          self).groundwork(request, args, kwargs)
        if error_url:
            return error_url
        self.manage_vol_url = reverse('manage_show_opp',
                                      urlconf='gbe.scheduling.urls',
                                      args=[kwargs['conference'],
                                            kwargs['occurrence_id']])
        self.success_url = reverse('edit_show',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.conference.conference_slug,
                                         self.occurrence.pk])

    def get_rehearsal_forms(self,
                            initial,
                            manage_slot_info,
                            conference,
                            request,
                            errorcontext=None,
                            occurrence_id=None):
        '''
        Generate the forms to allocate, edit, or delete volunteer
        opportunities associated with a scheduler event.
        '''
        actionform = []
        context = {}
        if occurrence_id is not None or len(labels) > 0:
            response = get_occurrences(parent_event_id=occurrence_id)
        else:
            return None

        for rehearsal_slot in response.occurrences:
            try:
                rehearsal = GenericEvent.objects.get(
                        eventitem_id=rehearsal_slot.foreign_event_id,
                        type="Rehearsal Slot")
                if (errorcontext and 'error_slot_form' in errorcontext and
                        errorcontext['error_slot_form'].instance == rehearsal):
                    actionform.append(errorcontext['error_slot_form'])
                else:
                    num_volunteers = rehearsal_slot.max_volunteer
                    date = rehearsal_slot.start_time.date()

                    time = rehearsal_slot.start_time.time
                    day = get_conference_day(
                        conference=rehearsal.e_conference,
                        date=date)
                    location = rehearsal_slot.location
                    if location:
                        room = location.room
                    elif self.occurrence.location:
                        room = self.occurrence.location.room

                    actionform.append(
                        RehearsalSlotForm(
                            instance=rehearsal,
                            initial={'opp_event_id': rehearsal.event_id,
                                     'opp_sched_id': rehearsal_slot.pk,
                                     'max_volunteer': num_volunteers,
                                     'day': day,
                                     'time': time,
                                     'location': room,
                                     },
                            )
                        )
            except:
                pass
        context['slotactionform'] = actionform
        if errorcontext and 'createslotform' in errorcontext:
            createform = errorcontext['createslotform']
        else:
            createform = RehearsalSlotForm(
                prefix='new_slot',
                initial=initial,
                conference=conference)

        actionheaders = ['Title',
                         '#',
                         'Duration',
                         'Day',
                         'Time',
                         'Location']
        context.update({'createslotform': createform,
                        'slotactionheaders': actionheaders,
                        'manage_slot_url': manage_slot_info}),
        return context

    def make_context(self, request, errorcontext=None):
        context = super(EditShowView,
                        self).make_context(request, errorcontext=errorcontext)
        initial_rehearsal_info = {
                'type':  "Rehearsal Slot",
                'duration': 1,
                'max_volunteer': 10,
                'day': get_conference_day(
                    conference=self.conference,
                    date=self.occurrence.starttime.date()),
                'time': (self.occurrence.starttime - timedelta(hours=4)
                         ).strftime("%H:%M:%S"),
                'location': self.occurrence.location,
                'occurrence_id': self.occurrence.pk, } 
        context.update(self.get_rehearsal_forms(
                initial_rehearsal_info,
                self.manage_vol_url,
                self.conference,
                request,
                errorcontext=errorcontext,
                occurrence_id=self.occurrence.pk))
        context['rehearsal_open'] = request.GET.get('rehearsal_open', False)
        return context

    def is_manage_opps(self, path):
        return "manage-opps" in path or "manage-show-opps" in path

    def do_additional_actions(self, request):
        response = None
        context = None
        if ('create_slot' in request.POST.keys()) or (
                'duplicate_slot' in request.POST.keys()):
            self.create = True
            if 'create_slot' in request.POST.keys():
                self.event_form = RehearsalSlotForm(
                    request.POST,
                    prefix='new_slot',
                    conference=self.conference)
            else:
                self.event_form = RehearsalSlotForm(
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
                context = {'createslotform': self.event_form}
        elif 'edit_slot' in request.POST.keys():
            self.event = get_object_or_404(
                GenericEvent,
                event_id=request.POST['opp_event_id'])
            self.event_form = RehearsalSlotForm(
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
                context = {'error_slot_form': self.event_form}
        elif 'delete_slot' in request.POST.keys():
            opp = get_object_or_404(
                GenericEvent,
                event_id=request.POST['opp_event_id'])
            title = opp.e_title
            opp.delete()
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DELETE_REHEARSAL_SUCCESS",
                defaults={
                    'summary': "Rehearsal Slot Deleted",
                    'description': rehearsal_delete_msg})
            messages.success(
                request,
                '%s<br>Title: %s' % (
                    user_message[0].description,
                    title))
            return HttpResponseRedirect(self.success_url)
        return self.check_success_and_return(request,
                                             response=response,
                                             errorcontext=context)
