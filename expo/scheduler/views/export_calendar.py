from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from scheduler.functions import calendar_export

@login_required
@never_cache
def export_calendar(request):
    '''
    View to export calendars, wrapped around calendar_export function.  
    Used to allow importing of the calendar information into other
    applications, such as Guidebook.
    '''
    #  TODO: Add ability to filter on a users schedule for things like
    #  volunteer shifts.

    conference = request.GET.get('conference', None)
    cal_format = request.GET.get('cal_format', 'gbook')
    event_types = request.GET.get('event_types', 'All')
    day = request.GET.get('day', None)

    if day == 'All':
        day = None

    calendar = calendar_export(conference, cal_format, event_types, day)

    return HttpResponse(calendar, content_type='text/csv')
