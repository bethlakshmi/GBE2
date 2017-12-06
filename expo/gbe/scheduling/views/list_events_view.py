from django.views.generic import View
from django.shortcuts import (
    render,
)
from django.http import Http404
from django.core.urlresolvers import reverse
from gbe.models import (
    Class,
    Event,
    GenericEvent,
    Show,
)
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    conference_slugs,
)
from scheduler.idd import get_occurrences
from gbe_forms_text import (
    list_text,
    list_titles,
)
from gbetext import (
    event_options,
    class_options,
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

    def get_events_list_by_type(self):
        event_type = self.event_type.lower()
        items = []
        if event_type == "all":
            return Event.get_all_events(self.conference)

        event_types = dict(event_options)
        class_types = dict(class_options)
        if event_type in map(lambda x: x.lower(), event_types.keys()):
            items = GenericEvent.objects.filter(
                type__iexact=event_type,
                visible=True,
                e_conference=self.conference).order_by('e_title')
        elif event_type in map(lambda x: x.lower, class_types.keys()):
            items = Class.objects.filter(
                accepted='3',
                visible=True,
                type__iexact=event_type,
                e_conference=self.conference).order_by('e_title')
        elif event_type == 'show':
            items = Show.objects.filter(
                e_conference=self.conference).order_by('e_title')
        elif event_type == 'class':
            items = Class.objects.filter(
                accepted='3',
                visible=True,
                e_conference=self.conference).exclude(
                    type='Panel').order_by('e_title')
        else:
            items = []
        return items

    def get(self, request, *args, **kwargs):
        context = self.setup(request, args, kwargs)
        items = self.get_events_list_by_type()
        events = []
        for item in items:
            response = get_occurrences(
                foreign_event_ids=[item.eventitem_id])
            events += [{
                'eventitem': item,
                'scheduled_events': response.occurrences,
                'detail': reverse('detail_view',
                                  urlconf='gbe.scheduling.urls',
                                  args=[item.eventitem_id])}]
        context['events'] = events
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ListEventsView, self).dispatch(*args, **kwargs)
