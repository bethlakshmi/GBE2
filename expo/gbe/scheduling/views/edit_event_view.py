from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import (
    Conference,
    Event,
    UserMessage,
)
from gbe.scheduling.forms import (
    EventBookingForm,
    PersonAllocationForm,
    ScheduleOccurrenceForm,
)
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from ticketing.forms import LinkBPTEventForm
from gbe.ticketing_idd_interface import create_bpt_event
from gbe.functions import (
    eligible_volunteers,
    get_conference_day,
    validate_perms
)
from gbetext import (
    create_ticket_event_success_msg,
    link_event_to_ticket_success_msg,
    no_tickets_found_msg,
)
from gbe_forms_text import (
    role_map,
    event_settings,
)
from scheduler.idd import get_occurrence


class EditEventView(View):
    template = 'gbe/scheduling/edit_event.tmpl'

    def groundwork(self, request, args, kwargs):
        if "conference" in kwargs:
            self.conference = get_object_or_404(
                Conference,
                conference_slug=kwargs['conference'])
        if "occurrence_id" in kwargs:
            result = get_occurrence(kwargs['occurrence_id'])
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

    def setup_ticket_links(self, request, new_event, ticket_form):
        ticket_list = ""
        for ticket_event in ticket_form.cleaned_data['bpt_events']:
            ticket_event.linked_events.add(new_event)
            ticket_event.save()
            ticket_list += "%s - %s, %s" % (
                ticket_event.bpt_event_id,
                ticket_event.title,
                ticket_list)
        if len(ticket_list) > 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="LINKED_TICKETS",
                defaults={
                    'summary': "Linked New Event to Tickets",
                    'description': link_event_to_ticket_success_msg})
            messages.success(
                request,
                user_message[0].description + ticket_list)

        if ticket_form.cleaned_data['bpt_event_id']:
            ticket_event, ticket_count = create_bpt_event(
                ticket_form.cleaned_data['bpt_event_id'],
                conference=self.conference,
                events=[new_event],
                display_icon=ticket_form.cleaned_data['display_icon'],
            )
            if ticket_event:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="NEW_TICKETING_EVENT",
                    defaults={
                        'summary': "Created New Ticked Event",
                        'description': create_ticket_event_success_msg})
                messages.success(
                    request,
                    "%s %s - %s, with %d tickets from BPT" % (
                        user_message[0].description,
                        ticket_event.bpt_event_id,
                        ticket_event.title,
                        ticket_count))
            if ticket_count == 0:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="NO_TICKETS_FOR_EVENT",
                    defaults={
                        'summary': "Tickets not found for BPT Event",
                        'description': no_tickets_found_msg, })
                messages.warning(
                    request,
                    user_message[0].description)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {}
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        context['event_form'] = EventBookingForm(
                instance=self.item)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=self.conference,
            open_to_public=True,
            initial={'duration': self.item.duration,
                     'max_volunteer': self.occurrence.max_volunteer,
                     'day': get_conference_day(
                        conference=self.conference,
                        date=self.occurrence.starttime.date()),
                     'time': self.occurrence.starttime.strftime("%H:%M:%S"),
                     'location': self.occurrence.location})
        context['worker_formset'] = self.make_formset(
            event_settings[self.item.type.lower()]['roles'])
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkBPTEventForm(initial={
                'conference': self.conference, })
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        if self.event_type == "show":
            context['second_form'] = ShowBookingForm(request.POST)
        else:
            context['second_form'] = GenericBookingForm(request.POST)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            request.POST,
            conference=self.conference)
        context['worker_formset'] = self.make_formset(
            ticketed_event_settings[self.event_type]['roles'],
            post=request.POST)
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkBPTEventForm(request.POST, initial={
                'conference': self.conference, })
        if context['second_form'].is_valid(
                ) and context['scheduling_form'].is_valid(
                ) and self.is_formset_valid(context['worker_formset']) and (
                not context['tickets'] or context['tickets'].is_valid()):
            new_event = context['second_form'].save(commit=False)
            new_event.duration = Duration(
                minutes=context['scheduling_form'].cleaned_data[
                    'duration']*60)
            new_event.save()
            response = self.book_event(context['scheduling_form'],
                                       context['worker_formset'],
                                       new_event)
            if context['tickets']:
                self.setup_ticket_links(request, new_event, context['tickets'])
            success = self.finish_booking(
                request,
                response,
                context['scheduling_form'].cleaned_data['day'].pk)
            if success:
                if request.POST.get('set_event') == 'Continue to Volunteer Opportunities':
                    raise Exception('here')
                else:
                    return success
        return render(request, self.template, context)
