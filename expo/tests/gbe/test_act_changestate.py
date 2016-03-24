import nose.tools as nt
from unittest import TestCase
from django.core.exceptions import PermissionDenied
from django.test.client import RequestFactory
from django.test import Client
from gbe.views import act_changestate
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
    ShowFactory,
)

from tests.factories.scheduler_factories import SchedEventFactory
from tests.contexts import ActTechInfoContext
from tests.functions.gbe_functions import grant_privilege
from scheduler.models import ResourceAllocation


class TestActChangestate(TestCase):
    '''Tests for act_changestate view'''

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.act = ActFactory()
        self.show = ShowFactory()
        self.sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Act Coordinator')

    def test_act_changestate_authorized_user(self):
        request = self.factory.get('act/changestate/%d' % self.act.pk)
        request.user = self.privileged_user
        response = act_changestate(request, self.act.pk)
        nt.assert_equal(response.status_code, 302)

    def test_act_changestate_post_accepted_act(self):
        context = ActTechInfoContext()
        prev_count1 = ResourceAllocation.objects.filter(
            event=context.sched_event).count()
        prev_count2 = ResourceAllocation.objects.filter(
            event=self.sched_event).count()
        request = self.factory.post('act/changestate/%d' % context.act.pk)
        request.POST = {'show': self.show.pk,
                        'accepted': '2'}
        request.user = self.privileged_user
        response = act_changestate(request, self.act.pk)
        nt.assert_equal(1,
                        ResourceAllocation.objects.filter(
                            event=self.sched_event).count()-prev_count2)

    @nt.raises(PermissionDenied)
    def test_act_changestate_unauthorized_user(self):
        request = self.factory.get('act/changestate/%d' % self.act.pk)
        request.user = ProfileFactory().user_object
        response = act_changestate(request, self.act.pk)
