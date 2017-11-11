from django.shortcuts import render
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status


def staff_area(request, area_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    opps = None
    area = None
    parent_response = get_occurrences(eventitem_id=area_id)
    if parent_response.occurrences:
        area = parent_response.occurrences[0]
        opps_response = get_occurrences(
            parent_event_id=parent_response.occurrences[0].pk)
        opps = opps_response.occurrences
        show_general_status(request, opps_response, "staff_area" )

    else:
        show_general_status(request, parent_response, "staff_area")

    return render(request,
                  'gbe/report/staff_area_schedule.tmpl',
                  {'opps': opps,
                   'area': area})
