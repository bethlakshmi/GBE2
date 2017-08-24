from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from gbetext import calendar_type as calendar_type_options
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    get_conference_days,
    conference_slugs,
)

class ShowCalendarView(View):
    template = 'gbe/scheduling/calendar.tmpl'
    @property

    def groundwork(self, request, args, kwargs):
        pass

    def get(self, request, *args, **kwargs):
        context = {}
        calendar_type = None
        conference = None
        day = None

        if "calendar_type" in kwargs:
            calendar_type = kwargs['calendar_type']
            if calendar_type not in calendar_type_options.values():
                raise Http404
        if "conference" in self.request.GET:
            conf_slug = self.request.GET.get('conference', None)
            conference = get_conference_by_slug(conf_slug)
        else:
            conference = get_current_conference()

        if "day" in self.request.GET:
            day = self.request.GET.get('day', None)

        context = {
            'calendar_type': calendar_type,
            'conference': conference,
            'conference_slugs': conference_slugs()
        }
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ShowCalendarView, self).dispatch(*args, **kwargs)
