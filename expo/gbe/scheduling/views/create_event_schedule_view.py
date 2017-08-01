from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import ScheduleSelectionForm
from scheduler.idd.create_occurrence import create_occurrence
from scheduler.views.functions import (
    get_event_display_info,
)
from gbe.scheduling.views.functions import (
    get_single_role,
    get_multi_role,
    get_start_time,
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
        try:
            self.item = Event.objects.get_subclass(pk=eventitem_id)
        except Event.DoesNotExist:
            raise Http404
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

        form = ScheduleSelectionForm(
            prefix='event',
            instance=self.item,
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
        event_form = ScheduleSelectionForm(
            request.POST,
            instance=self.item,
            prefix='event')
        if event_form.is_valid():
            event = event_form.save(commit=False)
            data = event_form.cleaned_data

            room = get_object_or_404(Room, name=data['location'])
            people = get_single_role(data)
            people += get_multi_role(data)
            max_volunteer = 0
            if data['max_volunteer']:
                max_volunteer = data['max_volunteer']
            start_time = get_start_time(data)

            response = create_occurrence(
                event.eventitem_id,
                start_time,
                max_volunteer,
                people=people,
                locations=[room],
                labels=[event.e_conference.conference_slug,
                        event.calendar_type])
            if response.occurrence:
                event_form.save()
            return HttpResponseRedirect(reverse('event_schedule',
                                                urlconf='scheduler.urls',
                                                args=[self.event_type]))
        else:
            return render(
                request,
                self.template,
                {'eventitem': self.eventitem_view,
                 'form': event_form,
                 'user_id': request.user.id,
                 'event_type': self.event_type})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateEventScheduleView, self).dispatch(*args, **kwargs)
