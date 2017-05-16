import nose.tools as nt
from django.test import (
    Client,
    TestCase,
)
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ActFactory,
    EmailTemplateSenderFactory,
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
    assert_email_recipient,
    assert_email_template_create,
    assert_email_template_used,
    grant_privilege,
    login_as,
)
from scheduler.models import ResourceAllocation


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

    def test_act_waitlist_sends_notification_makes_template(self):
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        assert_email_template_create(
            'act wait list',
            "Your act proposal has changed status to Wait List"
        )

    def test_act_waitlist_sends_notification_has_template(self):
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act wait list',
            template__subject="test template"
        )
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        assert_email_template_used(
            "test template", "actemail@notify.com")

    def test_act_accept_makes_template_per_show(self):
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data)
        assert_email_template_create(
            'act accepted - %s' % self.show.e_title.lower(),
            "Your act has been cast in %s" % self.show.e_title
        )

    def test_act_accept_has_template_per_show(self):
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act accepted - %s' % self.show.e_title.lower(),
            template__subject="test template"
        )
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data)
        assert_email_template_used(
            "test template", "actemail@notify.com")
        assert_email_recipient([(context.performer.contact.contact_email)])

    @override_settings(ADMINS=[('Admin', 'admin@mock.test')])
    @override_settings(DEBUG=True)
    def test_act_accept_sends_debug_to_admin(self):
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data)
        assert_email_recipient([('admin@mock.test')])
