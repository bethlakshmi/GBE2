from django.shortcuts import render
from django.views.decorators.cache import never_cache
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from gbe.models import Profile
from scheduler.idd import get_schedule
from gbe.ticketing_idd_interface import get_checklist_items


@never_cache
def personal_schedule_view(request):
    viewer_profile = validate_perms(request, 'any', require=True)

    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    else:
        conference = get_current_conference

    people = Profile.objects.filter(
        user_object__is_active=True).select_related()
    schedules = []

    for person in people:
        response = get_schedule(person.user_object,
                                labels=[conference.conference_slug])
        items = get_checklist_items(person, conference)
        if len(response.schedule_items) > 0 or len(items) > 0:
            schedules += [{'person': person,
                           'bookings': response.schedule_items,
                           'checklist_items': items}]

    sorted_sched = sorted(
        schedules,
        key=lambda schedule: schedule['person'].get_badge_name())
    return render(request,
                  'gbe/report/printable_schedules.tmpl',
                  {'schedules': sorted_sched,
                   'conference_slugs': conference_slugs(),
                   'conference': conference})
