from django.shortcuts import render
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status


def volunteer_type(request, conference_choice, eventitem_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    opps = None
    area = None
    collection = get_occurrences(labels=[conference_choice, 'Volunteer'])
    if parent_response.occurrences:
        area = parent_response.occurrences[0]
        opps_response = get_occurrences(
            parent_event_id=parent_response.occurrences[0].pk)
        opps = opps_response.occurrences
        show_general_status(request, opps_response, "staff_area" )

    else:
        show_general_status(request, parent_response, "staff_area")

    return render(request,
                  'gbe/report/volunteer_type.tmpl',
                  {'opps': opps,
                   'area': area})
