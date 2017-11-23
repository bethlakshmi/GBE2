from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import UserMessage
from gbe.scheduling.forms import (
    GenericBookingForm,
    ScheduleOccurrenceForm,
)
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from ticketing.forms import LinkBPTEventForm
from gbe.ticketing_idd_interface import create_bpt_event
from gbe.functions import validate_perms
from gbetext import (
    create_ticket_event_success_msg,
    link_event_to_ticket_success_msg,
    no_tickets_found_msg,
)


class TicketedClassWizardView(EventWizardView):
    template = 'gbe/scheduling/ticketed_class_wizard.tmpl'
    roles = ['Teacher', 'Volunteer', 'Staff Lead']
    default_event_type = "general"

    def groundwork(self, request, args, kwargs):
        context = super(TicketedClassWizardView,
                        self).groundwork(request, args, kwargs)
        self.event_type = kwargs['event_type']
        context['event_type'] = "%s Class" % self.event_type.title()
        context['second_title'] = "Make New Class"
        context['tickets'] = None
        return context

    def make_formset(self, post=None):
        if self.event_type == 'master':
            formset = super(TicketedClassWizardView, self).make_formset(
                ['Teacher', 'Volunteer',], post=post)
        else:
            formset = super(TicketedClassWizardView, self).make_formset(
                ['Staff Lead', 'Teacher', 'Volunteer',], post=post)
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
                    'description': no_tickets_found_msg })
                messages.warning(
                    request,
                    user_message[0].description)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = GenericBookingForm(
            initial={'e_conference':  self.conference,
                     'type': self.event_type.title()})
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=self.conference,
            open_to_public=True,
            initial={'duration': 1, })
        context['worker_formset'] = self.make_formset()
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkBPTEventForm(initial={
                'conference': self.conference,})
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = GenericBookingForm(request.POST)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            request.POST,
            conference=self.conference)
        context['worker_formset'] = self.make_formset(post=request.POST)
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkBPTEventForm(request.POST, initial={
                'conference': self.conference,})
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
                return success
        return render(request, self.template, context)
