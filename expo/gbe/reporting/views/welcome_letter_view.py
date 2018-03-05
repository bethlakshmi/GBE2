from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe.models import (
    Profile,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from scheduler.idd import get_schedule
from gbe.ticketing_idd_interface import get_checklist_items


class WelcomeLetterView(View):
    profiles = None

    def groundwork(self, request, args, kwargs):
        viewer_profile = validate_perms(request, 'any', require=True)

        if request.GET and request.GET.get('conf_slug'):
            self.conference = get_conference_by_slug(request.GET['conf_slug'])
        else:
            self.conference = get_current_conference()

        if "username" in kwargs:
            self.profiles = [get_object_or_404(
                Profile,
                user_object__username=kwargs['username'])]
        else:
            self.profiles = Profile.objects.filter(
                user_object__is_active=True).select_related()

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        schedules = []

        for person in self.profiles:
            response = get_schedule(
                person.user_object,
                labels=[self.conference.conference_slug])
            ticket_items, role_items = get_checklist_items(person,
                                                           self.conference)
            if len(response.schedule_items) > 0 or len(
                    role_items) > 0 or len(ticket_items) > 0:
                schedules += [{'person': person,
                               'bookings': response.schedule_items,
                               'ticket_items': ticket_items,
                               'role_items': role_items}]

        sorted_sched = sorted(
            schedules,
            key=lambda schedule: schedule['person'].get_badge_name())
        return render(request,
                      'gbe/report/printable_schedules.tmpl',
                      {'schedules': sorted_sched,
                       'conference_slugs': conference_slugs(),
                       'conference': self.conference})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WelcomeLetterView, self).dispatch(*args, **kwargs)
