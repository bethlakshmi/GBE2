import nose.tools as nt
from django.test import TestCase
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
from post_office.models import EmailTemplate
from django.core import mail


class TestActChangestate(TestCase):
    '''Tests for act_changestate view'''
    view_name = 'act_changestate'

    def setUp(self):
        self.client = Client()
        self.act = ActFactory()
        self.show = ShowFactory()
        self.sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Act Coordinator')
        self.data = {'show': self.show.pk,
                     'accepted': '2'}

    def test_act_changestate_authorized_user(self):

        url = reverse(self.view_name,
                      args=[self.act.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
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
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data=self.data)
        nt.assert_equal(1,
                        ResourceAllocation.objects.filter(
                            event=self.sched_event).count() - prev_count2)

    def test_act_changestate_unauthorized_user(self):
        context = ActTechInfoContext()
        # url = reverse('%s/%d' % (self.view_name, context.act.pk),
        #               urlconf='gbe.urls')
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')

        login_as(ProfileFactory(), self)
        response = self.client.post(url,
                                    data=self.data)

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
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data=self.data,
                                    follow=True)
        self.assertContains(
            response,
            "is booked for"
        )

    def test_act_reject_sends_notification_makes_template(self):
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        assert 1 == len(mail.outbox)
        msg = mail.outbox[0]
        expected_subject = \
            "Your act proposal has changed status to Wait List"
        assert msg.subject == expected_subject
        template = EmailTemplate.objects.get(name='act wait list')
        assert template.subject == expected_subject

    def test_act_reject_sends_notification_has_template(self):
        expected_subject = "test template"
        template = EmailTemplate.objects.create(
            name='act wait list',
            subject=expected_subject,
            content='test',
            html_content='test',
            )
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        assert 1 == len(mail.outbox)
        msg = mail.outbox[0]
        assert msg.subject == expected_subject
