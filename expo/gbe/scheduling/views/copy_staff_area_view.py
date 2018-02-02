from gbe.scheduling.views import CopyCollectionsView
from django.shortcuts import get_object_or_404
from scheduler.idd import (
    create_occurrence,
    get_occurrences,
)
from gbe.scheduling.views.functions import show_general_status
from gbe.models import StaffArea
from gbe.functions import validate_perms
from datetime import timedelta
from expo.settings import DATETIME_FORMAT
from django.utils.text import slugify
from datetime import datetime


class CopyStaffAreaView(CopyCollectionsView):
    permissions = ('Scheduling Mavens',)
    area = None

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        self.area = get_object_or_404(StaffArea,
                                      id=int(kwargs['staff_id']))
        self.start_day = self.area.conference.conferenceday_set.order_by(
            "day").first().day
        response = get_occurrences(labels=[
            self.area.slug,
            self.area.conference.conference_slug])
        self.children = response.occurrences
        show_general_status(request, response, self.__class__.__name__)

    def make_context(self, request, post=None):
        context = {
            'first_title': "Copying - %s" % self.area.title,
            'event_type': "Staff"}
        return super(CopyStaffAreaView, self).make_context(request,
                                                           context,
                                                           post)

    def get_copy_target(self, context):
        area =  get_object_or_404(
            StaffArea,
            id=context['copy_mode'].cleaned_data['target_event'])
        second_title = "Destination is %s: %s" % (
            area.conference.conference_slug,
            area.title)
        if area.conference == self.area.conference:
            delta = timedelta()
        else:
            delta = area.conference.conferenceday_set.order_by("day").first(
                ).day - self.start_day
        return second_title, delta

    def copy_root(self, request, delta, conference):
        new_area = self.area
        new_area.pk = None
        new_area.conference = conference
        new_area.staff_lead = None
        if conference == self.area.conference:
            now = datetime.now().strftime(DATETIME_FORMAT)
            new_area.title = "%s - New - %s" % (
                self.area.title,
                now)
            new_area.slug = "%s_new_%s" % (
                self.area.slug,
                slugify(now))
        new_area.save()
        return new_area

    def copy_event(self, occurrence, delta, conference, root=None):
        gbe_event_copy = occurrence.as_subtype
        gbe_event_copy.pk = None
        gbe_event_copy.event_id = None
        gbe_event_copy.eventitem_ptr_id = None
        gbe_event_copy.eventitem_id = None
        gbe_event_copy.e_conference = conference
        gbe_event_copy.save()
        labels = [conference.conference_slug,
                  gbe_event_copy.calendar_type]
        if root:
            labels += [root.slug]

        response = create_occurrence(
            gbe_event_copy.eventitem_id,
            occurrence.starttime + delta,
            max_volunteer=occurrence.max_volunteer,
            locations=[occurrence.location],
            labels=labels
        )
        return response

    def get_child_copy_settings(self, form):
        new_root = StaffArea.objects.get(
            id=form.cleaned_data['target_event'])
        target_day = new_root.conference.conferenceday_set.order_by(
            "day").first()
        delta = target_day.day - self.start_day
        conference = new_root.conference
        return (new_root, target_day, delta, conference)
