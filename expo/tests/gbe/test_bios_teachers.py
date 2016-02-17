from django.shortcuts import get_object_or_404
from django.http import Http404
import gbe.models as conf
import nose.tools as nt
from unittest import TestCase
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import bios_teachers
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ClassProposalFactory,
    ProfileFactory,
    PersonaFactory
)
from gbe.models import (
    Conference
)
from django.core.urlresolvers import reverse
from scheduler.models import Event as sEvent
from datetime import datetime, date, time
import pytz
from scheduler.models import (
    Worker,
    EventContainer
)
from tests.factories.scheduler_factories import ResourceAllocationFactory


class TestReviewProposalList(TestCase):
    '''Tests for bios_teachers view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory.create()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description'
                }

    def test_bios_teachers_authorized_user(self):
        proposal = ClassProposalFactory.create()
        request = self.factory.get('bios/teachers/')
        request.user = ProfileFactory.create().user_object
        request.session = {'cms_admin_site': 1}
        response = bios_teachers(request)
        nt.assert_equal(response.status_code, 200)


def test_view_teachers_given_slug():
    '''/bios/teachers/ should return all teachers in the selected
    conference, given the conference slug in the get request'''
    conf = ConferenceFactory.create()
    other_conf = ConferenceFactory.create()
    this_class = ClassFactory.create(accepted=3)
    this_class.conference = conf
    this_class.title = "xyzzy"
    this_class.save()
    that_class = ClassFactory.create(accepted=3)
    that_class.conference = other_conf
    that_class.title = "plugh"
    that_class.save()
    this_sched_class = sEvent(
        eventitem=this_class,
        starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
    this_sched_class.save()
    worker = Worker(_item=this_class.teacher, role='Teacher')
    worker.save()
    this_class_assignment = ResourceAllocationFactory.create(
            event=this_sched_class,
            resource=worker
    )
    this_class_assignment.save()
    that_sched_class = sEvent(
        eventitem=that_class,
        starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
    that_sched_class.save()
    that_worker = Worker(_item=that_class.teacher, role='Teacher')
    that_worker.save()
    that_class_assignment = ResourceAllocationFactory.create(
            event=that_sched_class,
            resource=that_worker
    )
    that_class_assignment.save()

    request = RequestFactory().get(
        reverse("bios_teacher",
                urlconf="gbe.urls"),
        data={"conference": conf.conference_slug})
    request.user = ProfileFactory.create().user_object
    request.session = {'cms_admin_site': 1}
    response = bios_teachers(request)
    nt.assert_true(this_class.title in response.content)
    nt.assert_false(that_class.title in response.content)


def test_view_teachers_default_view_current_conf_exists():
    '''/bios/teachers/ should return all teachers in the current
    conference, assuming a current conference exists'''
    Conference.objects.all().delete()
    conf = ConferenceFactory.create()
    other_conf = ConferenceFactory.create(status='completed')
    accepted_class = ClassFactory(accepted=3)
    accepted_class.conference = conf
    accepted_class.title = 'accepted'
    accepted_class.save()
    previous_class = ClassFactory(accepted=3)
    previous_class.conference = other_conf
    previous_class.title = 'previous'
    previous_class.save()
    rejected_class = ClassFactory(accepted=1)
    rejected_class.conference = conf
    rejected_class.title = 'reject'
    rejected_class.save()

    accepted_sched_class = sEvent(
        eventitem=accepted_class,
        starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
    accepted_sched_class.save()
    worker = Worker(_item=accepted_class.teacher, role='Teacher')
    worker.save()
    accepted_class_assignment = ResourceAllocationFactory.create(
            event=accepted_sched_class,
            resource=worker
    )
    accepted_class_assignment.save()

    previous_sched_class = sEvent(
        eventitem=previous_class,
        starttime=datetime(2016, 2, 6, 9, 0, 0, 0, pytz.utc))
    previous_sched_class.save()
    previous_worker = Worker(_item=previous_class.teacher, role='Teacher')
    previous_worker.save()
    previous_class_assignment = ResourceAllocationFactory.create(
            event=previous_sched_class,
            resource=previous_worker
    )
    previous_class_assignment.save()

    request = RequestFactory().get(
        reverse("bios_teacher",
                urlconf="gbe.urls"))
    request.user = ProfileFactory.create().user_object
    request.session = {'cms_admin_site': 1}
    response = bios_teachers(request)
    nt.assert_true(accepted_class.title in response.content)
    nt.assert_false(rejected_class.title in response.content)
    nt.assert_false(previous_class.title in response.content)
