from django.shortcuts import render
from django.shortcuts import get_object_or_404
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import StaffArea

def staff_area_view(request, area_id):
    '''
    Generates a staff area report: volunteer opportunities scheduled,
    volunteers scheduled, sorted by time/day
    See ticket #250
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    opps = None
    area = get_object_or_404(StaffArea, pk=area_id)
    opps_response = get_occurrences(labels=[
        area.conference.conference_slug,
        area.slug])
    opps = opps_response.occurrences
    show_general_status(request, opps_response, "staff_area")

    return render(request,
                  'gbe/report/staff_area_schedule.tmpl',
                  {'opps': opps,
                   'area': area})
