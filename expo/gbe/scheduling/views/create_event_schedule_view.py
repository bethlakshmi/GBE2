from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
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
from gbe.models import (
    Event,
    Room
)
from gbe.functions import validate_perms
from gbe.duration import Duration
from gbe.views.class_display_functions import get_scheduling_info


class CreateEventScheduleView(View):
    template = 'scheduler/event_schedule.tmpl'

    def groundwork(self, request, args, kwargs):
        eventitem_id = kwargs['eventitem_id']
        self.event_type = kwargs['event_type'] or 'Class'
        self.profile = validate_perms(request, ('Scheduling Mavens',))
        self.item = Event.objects.get_subclass(pk=eventitem_id)
        self.eventitem_view = get_event_display_info(eventitem_id)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        scheduling_info = {}
        initial_form_info = {'duration': self.item.duration,
                             'description': self.item.e_description,
                             'title': self.item.e_title,
                             'location': self.item.default_location}

        if self.item.__class__.__name__ == 'Class':
            initial_form_info['teacher'] = self.item.teacher
            initial_form_info['duration'] = Duration(
                self.item.duration.days,
                self.item.duration.seconds)
            scheduling_info = get_scheduling_info(self.item)

        form = EventScheduleForm(prefix='event',
                                 initial=initial_form_info)

        return render(
            request,
            self.template,
            {'eventitem': self.eventitem_view,
             'form': form,
             'user_id': request.user.id,
             'event_type': self.event_type,
             'scheduling_info': scheduling_info})

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        event_form = EventScheduleForm(request.POST,
                                       prefix='event')
        if event_form.is_valid():
            s_event = event_form.save(commit=False)
            s_event.eventitem = self.item
            data = event_form.cleaned_data

            if data['duration']:
                s_event.set_duration(data['duration'])

            l = get_object_or_404(Room, name=data['location'])
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
                                                args=[self.event_type]))
        else:
            return render(
                request,
                self.template,
                {'eventitem': eventitem_view,
                 'form': event_form,
                 'user_id': request.user.id,
                 'event_type': self.event_type})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateEventScheduleView, self).dispatch(*args, **kwargs)
