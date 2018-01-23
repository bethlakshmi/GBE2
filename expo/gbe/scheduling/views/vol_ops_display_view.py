from django.views.generic import View
from gbe.models import Event
from gbe.scheduling.forms import VolunteerOpportunityForm
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
)
from scheduler.idd import get_occurrences


class VolOpsDisplayView(View):
    template = 'gbe/scheduling/edit_event.tmpl'

    def get_manage_opportunity_forms(self,
                                     initial,
                                     occurrence_id,
                                     manage_vol_info,
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
                        'manage_vol_url': manage_vol_info}),
        return context
