from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from scheduler.forms import EventScheduleForm
from scheduler.views.functions import (
    get_event_display_info,
    set_single_role,
    set_multi_role,
)
from scheduler.models import (
    EventItem,
    LocationItem,
)
from gbe.functions import validate_perms
from gbe.duration import Duration
from django.views.decorators.cache import never_cache
from gbe.views.class_display_functions import get_scheduling_info


@login_required
@never_cache
def add_event(request, eventitem_id, event_type='Class'):
    '''
    Add an item to the conference schedule and/or set its schedule details
    (start time, location, duration, or allocations)
    Takes a scheduler.EventItem id - BB - separating new event from editing
    existing, so that edit can identify particular schedule items, while this
    identifies the event item.
    '''
    profile = validate_perms(request, ('Scheduling Mavens',))
    template = 'scheduler/event_schedule.tmpl'
    eventitem = get_object_or_404(EventItem, eventitem_id=eventitem_id)
    item = eventitem.child()
    eventitem_view = get_event_display_info(eventitem_id)

    if request.method == 'POST':
        return handle_post(request, template, eventitem_view, event_type, item)
    else:
        return handle_get(request, template, eventitem_view, event_type, item)


def handle_get(request, template, eventitem_view, event_type, item):
    scheduling_info = {}
    initial_form_info = {'duration': item.duration,
                         'description': item.sched_payload['description'],
                         'title': item.sched_payload['title'],
                         'location': item.default_location}
    if item.__class__.__name__ == 'Class':
        initial_form_info['teacher'] = item.teacher
        initial_form_info['duration'] = Duration(item.duration.days,
                                                 item.duration.seconds)
        scheduling_info = get_scheduling_info(item)

    form = EventScheduleForm(prefix='event',
                             initial=initial_form_info)

    return render(request, template, {'eventitem': eventitem_view,
                                      'form': form,
                                      'user_id': request.user.id,
                                      'event_type': event_type,
                                      'scheduling_info': scheduling_info})


def handle_post(request, template, eventitem_view, event_type, item):
    event_form = EventScheduleForm(request.POST,
                                   prefix='event')
    if event_form.is_valid():
        s_event = event_form.save(commit=False)
        s_event.eventitem = item
        data = event_form.cleaned_data

        if data['duration']:
            s_event.set_duration(data['duration'])

        l = LocationItem.objects.get_subclass(room__name=data['location'])
        s_event.save()
        s_event.set_location(l)
        set_single_role(s_event, data)
        set_multi_role(s_event, data)
        if data['description'] or data['title']:
            c_event = s_event.as_subtype
            c_event.description = data['description']
            c_event.title = data['title']
            c_event.save()

        return HttpResponseRedirect(reverse('event_schedule',
                                            urlconf='scheduler.urls',
                                            args=[event_type]))
    else:
        return render(request, template, {'eventitem': eventitem_view,
                                          'form': event_form,
                                          'user_id': request.user.id,
                                          'event_type': event_type})
