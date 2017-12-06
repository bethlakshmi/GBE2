from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.formats import date_format
from expo.settings import (
    DATE_FORMAT,
    DATETIME_FORMAT,
    TIME_FORMAT,
    URL_DATE,
)
from datetime import (
    datetime,
    timedelta,
)
from gbe.models import (
    AvailableInterest,
    ConferenceDay,
    Event,
    GenericEvent,
)
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    get_events_list_by_type,
    conference_slugs,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.forms import (
    HiddenSelectEventForm,
    SelectEventForm,
)
from datetime import datetime
from gbe_forms_text import (
    list_text,
    list_titles,
)


class ListEventsView(View):
    template = 'gbe/scheduling/event_display_list.tmpl'
    conference = None
    event_type = "All"

    def setup(self, request, args, kwargs):
        context = {}

        if "event_type" in kwargs:
            self.event_type = kwargs['event_type']
            if self.event_type.lower() not in list_titles:
                raise Http404

        if "conference" in self.request.GET:
            self.conference = get_conference_by_slug(
                self.request.GET.get('conference', None))
        else:
            self.conference = get_current_conference()
        if not self.conference:
            raise Http404

        context = {
            'conf_slug': self.conference.conference_slug,
            'conference_slugs': conference_slugs(),
            'title': list_titles.get(self.event_type.lower(), ""),
            'view_header_text': list_text.get(self.event_type.lower(), ""),
            'etype': self.event_type,
        }

        return context

    def get(self, request, *args, **kwargs):
        context = self.setup(request, args, kwargs)

        items = get_events_list_by_type(self.event_type, self.conference)
        events = [
            {'eventitem': item,
             'scheduled_events': item.scheduler_events.order_by('starttime'),
             'detail': reverse('detail_view',
                               urlconf='gbe.scheduling.urls',
                               args=[item.eventitem_id])
             }
            for item in items]
        context['events'] = events
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ListEventsView, self).dispatch(*args, **kwargs)
