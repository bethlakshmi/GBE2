from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.formats import date_format
from expo.settings import (
    TIME_FORMAT,
    URL_DATE,
)
from datetime import (
    datetime,
    timedelta,
)
from gbe.models import (
    ConferenceDay,
    Event,
)
from gbe.functions import (
    get_current_conference,
    get_conference_days,
    get_conference_by_slug,
    conference_slugs,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.scheduling.forms import SelectEventForm
from expo.settings import DATE_FORMAT
from datetime import datetime


class ManageEventsView(View):
    template = 'gbe/scheduling/manage_event.tmpl'
    calendar_type = None
    conference = None
    this_day = None

    def make_context(self, request, args, kwargs):
        context = {}
        self.calendar_type = None
        self.conference = None
        self.this_day = None

        if "conference_slug" in kwargs:
            self.conference = get_conference_by_slug(
                kwargs['conference_slug'])
        else:
            self.conference = get_current_conference()

        self.select_form = SelectEventForm(prefix="event-select")
        day_list = []
        for day in self.conference.conferenceday_set.all():
            day_list += [(day.pk, day.day.strftime(DATE_FORMAT))]
        self.select_form.fields['day'].choices = day_list

        context = {
            'conference': self.conference,
            'conference_slugs': conference_slugs(),
            'selection_form': self.select_form,
        }

        return context

    def get(self, request, *args, **kwargs):
        context = self.make_context(request, args, kwargs)
        search_labels = [self.conference.conference_slug, ]
        response = get_occurrences(
            labels=search_labels)
        show_general_status(
            request, response, self.__class__.__name__)

        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        pass

    def dispatch(self, *args, **kwargs):
        return super(ManageEventsView, self).dispatch(*args, **kwargs)
