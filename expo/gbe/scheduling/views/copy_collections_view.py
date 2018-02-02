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
from gbe.scheduling.forms import (
    CopyEventForm,
    CopyEventPickDayForm,
    CopyEventPickModeForm,
)
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    get_occurrences,
)
from gbe.scheduling.views.functions import (
    show_general_status,
    show_scheduling_occurrence_status,
)
from gbe.models import (
    Conference,
    ConferenceDay,
    Event,
)
from gbe.functions import validate_perms
from gbe.duration import Duration
from gbe.views.class_display_functions import get_scheduling_info
from datetime import timedelta


class CopyCollectionsView(View):
    '''
        This is an abstract view to help with copying, and remove redundant
        code.  Child views are required to have:
        - a groundwork function that creates a list of self.children, a
          start_day and checks permissions
        - a make_context that defines the first title and event_type
        - get_copy_target = returning the second title and the delta days
    '''
    template = 'gbe/scheduling/copy_wizard.tmpl'
    permissions = ('Scheduling Mavens',)
    copy_date_format = "%a, %b %-d, %Y %-I:%M %p"
    occurrence = None
    children = []
    future_days = None

    def make_context(self, request, context, post=None):
        if self.children and len(self.children) > 0:
            context['copy_mode'] = CopyEventPickModeForm(
                post,
                event_type=context['event_type'])
        else:
            context['pick_day'] = CopyEventPickDayForm(post)
            context['pick_day'].fields['copy_to_day'].empty_label = None
            context['pick_day'].fields['copy_to_day'].required = True
        return context

    def validate_and_proceed(self, request, context):
        make_copy = False
        if 'copy_mode' in context.keys() and context['copy_mode'].is_valid():
            if context['copy_mode'].cleaned_data[
                    'copy_mode'] == "copy_children_only":
                context['second_title'], delta = self.get_copy_target(context)
            elif context['copy_mode'].cleaned_data[
                    'copy_mode'] == "include_parent":
                context['second_title'] = "Create Copy at %s: %s" % (
                    context['copy_mode'].cleaned_data[
                        'copy_to_day'].conference.conference_slug,
                    str(context['copy_mode'].cleaned_data['copy_to_day']))
                delta = context['copy_mode'].cleaned_data[
                    'copy_to_day'].day - self.start_day
            context['second_form'] = self.make_event_picker(
                request,
                delta)
        elif 'pick_day' in context.keys() and context['pick_day'].is_valid():
            make_copy = True
        return make_copy, context

    def make_event_picker(self, request, delta):
        form = CopyEventForm(request.POST)
        event_choices = ()
        for occurrence in self.children:
            event_choices += ((
                occurrence.pk,
                "%s - %s" % (
                    str(occurrence),
                    (occurrence.start_time + delta).strftime(
                        self.copy_date_format))),)
        form.fields['copied_event'].choices = event_choices
        return form

    def copy_events_from_form(self, request):
        form = self.make_event_picker(request, timedelta(0))
        new_root = None
        if form.is_valid():
            copied_ids = []
            alt_id = None
            if form.cleaned_data['copy_mode'] == "copy_children_only":
                (new_root,
                 target_day,
                 delta,
                 conference) = self.get_child_copy_settings(form)
            elif form.cleaned_data['copy_mode'] == "include_parent":
                target_day = form.cleaned_data['copy_to_day']
                delta = target_day.day - self.start_day
                conference = form.cleaned_data['copy_to_day'].conference
                new_root = self.copy_root(
                    request,
                    delta,
                    form.cleaned_data['copy_to_day'].conference)
                if new_root and new_root.__class__.__name__ == "Event":
                    copied_ids += [new_root.pk]
                else:
                    alt_id = new_root.pk

            for sub_event_id in form.cleaned_data["copied_event"]:
                response = get_occurrence(sub_event_id)
                response = self.copy_event(
                    response.occurrence,
                    delta,
                    conference,
                    new_root)
                show_scheduling_occurrence_status(
                    request,
                    response,
                    self.__class__.__name__)
                if response.occurrence:
                    copied_ids += [response.occurrence.pk]
            url = "%s?%s-day=%d&filter=Filter" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[conference.conference_slug]),
                conference.conference_slug,
                target_day.pk)
            if len(copied_ids) > 0:
                url += "&new=%s" % str(copied_ids)
            if alt_id:
                url += "&alt_id=%s" % alt_id
            return HttpResponseRedirect(url)
        else:
            context = self.make_context(request, post=request.POST)
            make_copy, context = self.validate_and_proceed(request, context)
            context['second_form'] = form
            return render(request, self.template, context)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return render(
            request,
            self.template,
            self.make_context(request))

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        context = {}
        if 'pick_mode' in request.POST.keys():
            context = self.make_context(request, post=request.POST)
            make_copy, context = self.validate_and_proceed(request, context)
            if make_copy:
                target_day = context['pick_day'].cleaned_data[
                    'copy_to_day']
                delta = target_day.day - self.start_day
                response = self.copy_event(
                    self.occurrence,
                    delta,
                    target_day.conference)
                show_scheduling_occurrence_status(
                    request,
                    response,
                    self.__class__.__name__)
                if response.occurrence:
                    slug = target_day.conference.conference_slug
                    return HttpResponseRedirect(
                        "%s?%s-day=%d&filter=Filter&new=%s" % (
                            reverse('manage_event_list',
                                    urlconf='gbe.scheduling.urls',
                                    args=[slug]),
                            slug,
                            target_day.pk,
                            str([response.occurrence.pk]),))
        if 'pick_event' in request.POST.keys():
            return self.copy_events_from_form(request)
        return render(
            request,
            self.template,
            context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CopyCollectionsView, self).dispatch(*args, **kwargs)
