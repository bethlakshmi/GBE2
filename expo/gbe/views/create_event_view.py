from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from expo.gbe_logging import log_func
from gbe.models import Conference
from gbe.functions import validate_perms
from gbe.forms.schedule import (
    GenericEventScheduleForm,
    ShowScheduleForm,
    ClassScheduleForm,
)
from gbe_forms_text import event_create_text


@log_func
def CreateEventView(request, event_type):
    scheduler = validate_perms(request, ('Scheduling Mavens',))
    page_title = "Create " + event_type
    view_title = page_title
    submit_button = "Create " + event_type

    if request.method == 'POST':
        form = eval(event_type+"ScheduleForm")(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.e_conference = Conference.objects.filter(
                status='upcoming').first()
            event.save()
            return HttpResponseRedirect(reverse('event_schedule',
                                                urlconf='scheduler.urls',
                                                args=[event_type]))
        else:
            return render(request, 'gbe/bid.tmpl',
                          {'forms': [form],
                           'nodraft': submit_button,
                           'page_title': page_title,
                           'view_title': view_title,
                           'view_header_text': event_create_text[event_type]})
    else:
        form = eval(event_type+"ScheduleForm")

        return render(request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       'view_header_text': event_create_text[event_type]})
