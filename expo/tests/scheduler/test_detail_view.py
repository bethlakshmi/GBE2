import pytest
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django import forms
import nose.tools as nt
from django.test.client import RequestFactory
from django.test import Client
from scheduler.views import detail_view
from scheduler.forms import conference_days
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)


def schedule_show(show):
    return SchedEventFactory.create(eventitem=show.eventitem_ptr)


@pytest.mark.django_db
def test_no_permission_required():
    show = ShowFactory()
    sched_event = schedule_show(show)
    request = RequestFactory().get(
        '/scheduler/details/%d' % show.eventitem_ptr.pk)
    request.user = ProfileFactory().user_object
    request.session = {'cms_admin_site': 1}
    response = detail_view(request, show.eventitem_ptr.pk)
    nt.assert_equal(200, response.status_code)
    nt.assert_true(show.title in response.content)


@pytest.mark.django_db
@nt.raises(Http404)
def test_bad_id_raises_404():
    request = RequestFactory().get(
        '/scheduler/details/%d' % -1)
    request.user = ProfileFactory.user_object
    request.session = {'cms_admin_site': 1}
    response = detail_view(request, -1)


@pytest.mark.django_db
def test_repeated_lead_shows_once():
    show = ShowFactory()
    sched_events = [schedule_show(show) for i in range(2)]
    staff_lead = ProfileFactory()
    lead_worker = WorkerFactory(_item=staff_lead.workeritem_ptr,
                                role="Staff Lead")
    for se in sched_events:
        ResourceAllocationFactory.create(event=se,
                                         resource=lead_worker)
    request = RequestFactory().get(
        '/scheduler/details/%d' % show.eventitem_ptr.pk)
    request.user = ProfileFactory().user_object
    request.session = {'cms_admin_site': 1}
    response = detail_view(request, show.eventitem_ptr.pk)
    nt.assert_equal(200, response.status_code)
    nt.assert_equal(1, response.content.count(staff_lead.display_name))
