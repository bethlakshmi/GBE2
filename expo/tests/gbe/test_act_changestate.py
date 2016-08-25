import nose.tools as nt
from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from tests.contexts import ActTechInfoContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from scheduler.models import ResourceAllocation


class TestActChangestate(TestCase):
    '''Tests for act_changestate view'''
    view_name = 'act_changestate'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.act = ActFactory()
        self.show = ShowFactory()
        self.sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Act Coordinator')

    def test_act_changestate_authorized_user(self):

        url = reverse(self.view_name,
                      args=[self.act.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url, args=[self.act.pk])
#        import pdb; pdb.set_trace()
        nt.assert_equal(response.status_code, 302)

    def test_act_changestate_post_accepted_act(self):
        context = ActTechInfoContext()
        prev_count1 = ResourceAllocation.objects.filter(
            event=context.sched_event).count()
        prev_count2 = ResourceAllocation.objects.filter(
            event=self.sched_event).count()
        # url = reverse('%s/%d' % (self.view_name, context.act.pk),
        #               urlconf='gbe.urls')
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        data = {'show': self.show.pk,
                'accepted': '2'}
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data=data)
        nt.assert_equal(1,
                        ResourceAllocation.objects.filter(
                            event=self.sched_event).count()-prev_count2)

    def test_act_changestate_unauthorized_user(self):
        context = ActTechInfoContext()
        # url = reverse('%s/%d' % (self.view_name, context.act.pk),
        #               urlconf='gbe.urls')
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')

        data = {'show': self.show.pk,
                'accepted': '2'}
        login_as(ProfileFactory(), self)
        response = self.client.post(url,
                                    data=data)

        nt.assert_equal(403, response.status_code)

    def test_act_changestate_book_act_with_conflict(self):
        context = ActTechInfoContext()
        grant_privilege(self.privileged_user, 'Act Reviewers')
        conflict = SchedEventFactory(
            starttime=context.sched_event.starttime)
        ResourceAllocationFactory(
            event=conflict,
            resource=WorkerFactory(_item=context.performer.performer_profile)
        )
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        data = {'show': self.show.pk,
                'accepted': '2'}
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertContains(
            response,
            "is booked for"
        )
