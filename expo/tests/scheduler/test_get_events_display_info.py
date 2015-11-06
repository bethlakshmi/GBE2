from django.http import Http404
from django import forms
from gbe.models import Conference
import nose.tools as nt
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory
)
from scheduler.views import get_events_display_info


def test_get_events_display_info_active_conference():
    for conference in Conference.objects.all():
        conference.status = "completed"
        conference.save()
    conference = ConferenceFactory.create()
    conference.status = "upcoming"
    conference.save()
    cls = ClassFactory.create(conference=conference)
    cls.accepted = 3
    cls.save()
    eventslist = get_events_display_info()
    nt.assert_equal(len(eventslist), 1)


def test_get_events_display_info_conference_not_active():
    conference = ConferenceFactory.create()
    cls = ClassFactory.create(conference=conference)
    for conference in Conference.objects.all():
        conference.status = "completed"
        conference.save()
    cls.accepted = 3
    cls.save()
    eventslist = get_events_display_info()
    nt.assert_equal(len(eventslist), 0)
