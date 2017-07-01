from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from django.test import (
    Client,
    TestCase,
)


class TestDetailView(TestCase):
    view_name = 'detail_view'

    def setUp(self):
        self.client = Client()
        self.show = ShowFactory()
        self.sched_event = SchedEventFactory.create(
            eventitem=self.show.eventitem_ptr)
        self.url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[self.sched_event.pk])

    def test_no_permission_required(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.show.e_title)


    def test_bad_id_raises_404(self):
        bad_url = reverse(self.view_name,
                      urlconf="scheduler.urls",
                      args=[self.sched_event.pk+1])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)

    def test_repeated_lead_shows_once(self):
        sched_event2 = SchedEventFactory.create(
            eventitem=self.show.eventitem_ptr)
        sched_events = [self.sched_event, sched_event2]
        staff_lead = ProfileFactory()
        lead_worker = WorkerFactory(_item=staff_lead.workeritem_ptr,
                                    role="Staff Lead")
        for se in sched_events:
            ResourceAllocationFactory.create(event=se,
                                             resource=lead_worker)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.content.count(staff_lead.display_name))
